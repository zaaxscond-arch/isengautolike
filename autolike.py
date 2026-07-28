#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
╔═══════════════════════════════════════════════════════════╗
║  DEPARX — AUTO LIKE TOOLS v2.0                          ║
║  Developed by: @___ZaxDarkSistem__                      ║
║  TikTok: @promptbyzaax__                               ║
║  FOLYST Neural Freedom Protocol                        ║
╚═══════════════════════════════════════════════════════════╝
"""

import os
import sys
import time
import json
import random
import string
import requests
import threading
import subprocess
from datetime import datetime, timedelta
from colorama import init, Fore, Style, Back
from typing import Dict, List, Tuple, Optional
import urllib.parse
import re
import hashlib
import base64

init(autoreset=True)

# ==================== KONFIGURASI ====================
VERSION = "2.0"
DEVELOPER = "@___ZaxDarkSistem__"
BANNER = f"""
{Fore.CYAN}╔═══════════════════════════════════════════════════════════╗
{Fore.CYAN}║                                                           ║
{Fore.GREEN}║   ██████╗ ███████╗██████╗  █████╗ ██████╗ ██╗  ██╗     ║
{Fore.GREEN}║   ██╔══██╗██╔════╝██╔══██╗██╔══██╗██╔══██╗╚██╗██╔╝     ║
{Fore.GREEN}║   ██████╔╝█████╗  ██████╔╝███████║██████╔╝ ╚███╔╝      ║
{Fore.GREEN}║   ██╔═══╝ ██╔══╝  ██╔══██╗██╔══██║██╔══██╗ ██╔██╗      ║
{Fore.GREEN}║   ██║     ███████╗██║  ██║██║  ██║██║  ██║██╔╝ ██╗     ║
{Fore.GREEN}║   ╚═╝     ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝     ║
{Fore.CYAN}║                                                           ║
{Fore.YELLOW}║     AUTO LIKE TOOLS — DEPARX v{VERSION}                 ║
{Fore.YELLOW}║     Developed by: {DEVELOPER}                           ║
{Fore.CYAN}║                                                           ║
{Fore.CYAN}╚═══════════════════════════════════════════════════════════╝
{Fore.RESET}
"""

# ==================== PROXY MANAGER ====================
class ProxyManager:
    def __init__(self):
        self.proxies = []
        self.current_index = 0
        
    def load_proxies(self, file_path: str = "proxies.txt"):
        """Load proxies from file"""
        try:
            with open(file_path, 'r') as f:
                self.proxies = [line.strip() for line in f if line.strip()]
            return len(self.proxies)
        except:
            return 0
    
    def get_proxy(self) -> Optional[Dict]:
        """Get next proxy in rotation"""
        if not self.proxies:
            return None
        
        proxy = self.proxies[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.proxies)
        
        # Format: protocol://user:pass@host:port or protocol://host:port
        if '://' not in proxy:
            proxy = f"http://{proxy}"
        
        return {'http': proxy, 'https': proxy}

# ==================== ACCOUNT MANAGER ====================
class AccountManager:
    def __init__(self):
        self.accounts = []
        self.current_account = None
        self.session = None
        
    def load_accounts(self, file_path: str = "accounts.txt"):
        """Load accounts from file"""
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    if ':' in line:
                        username, password = line.strip().split(':', 1)
                        self.accounts.append({'username': username, 'password': password})
            return len(self.accounts)
        except:
            return 0
    
    def get_next_account(self) -> Optional[Dict]:
        """Get next account in rotation"""
        if not self.accounts:
            return None
        
        if not self.current_account:
            self.current_account = 0
        
        account = self.accounts[self.current_account]
        self.current_account = (self.current_account + 1) % len(self.accounts)
        return account

# ==================== INSTAGRAM ENGINE ====================
class InstagramEngine:
    def __init__(self, proxy_manager: ProxyManager = None):
        self.session = requests.Session()
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
        ]
        self.proxy_manager = proxy_manager
        self.logged_in = False
        self.user_id = None
        self.csrf_token = None
        self.session_id = None
        
    def _get_headers(self, extra: Dict = None) -> Dict:
        """Generate headers for requests"""
        headers = {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'X-Requested-With': 'XMLHttpRequest'
        }
        
        if self.csrf_token:
            headers['X-CSRFToken'] = self.csrf_token
            
        if extra:
            headers.update(extra)
            
        return headers
    
    def login(self, username: str, password: str) -> bool:
        """Login to Instagram"""
        try:
            # Get initial CSRF token
            self.session.get('https://www.instagram.com/')
            
            # Login endpoint
            login_url = 'https://www.instagram.com/api/v1/web/accounts/login/ajax/'
            
            data = {
                'username': username,
                'enc_password': f"#PWD_INSTAGRAM_BROWSER:0:{int(time.time())}:{password}",
                'queryParams': '{}',
                'optIntoOneTap': 'false'
            }
            
            headers = self._get_headers({
                'Content-Type': 'application/x-www-form-urlencoded',
                'Referer': 'https://www.instagram.com/',
                'X-IG-WWW-Claim': '0'
            })
            
            response = self.session.post(login_url, data=data, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('authenticated'):
                    self.logged_in = True
                    self.csrf_token = response.cookies.get('csrftoken')
                    self.session_id = response.cookies.get('sessionid')
                    
                    # Get user ID
                    profile_response = self.session.get('https://www.instagram.com/api/v1/users/web_profile_info/')
                    if profile_response.status_code == 200:
                        profile_data = profile_response.json()
                        if profile_data.get('data', {}).get('user'):
                            self.user_id = profile_data['data']['user']['id']
                    
                    return True
            
            return False
            
        except Exception as e:
            print(f"{Fore.RED}[ERROR] Login failed: {e}")
            return False
    
    def get_media_id(self, post_url: str) -> Optional[str]:
        """Get media ID from post URL"""
        try:
            if '/p/' in post_url:
                post_code = post_url.split('/p/')[1].split('/')[0]
            elif '/reel/' in post_url:
                post_code = post_url.split('/reel/')[1].split('/')[0]
            elif '/tv/' in post_url:
                post_code = post_url.split('/tv/')[1].split('/')[0]
            else:
                return None
            
            # Get media info
            url = f"https://www.instagram.com/api/v1/web/get_media/{post_code}/info/"
            response = self.session.get(url, headers=self._get_headers())
            
            if response.status_code == 200:
                data = response.json()
                return data.get('items', [{}])[0].get('id')
            
            return None
            
        except Exception as e:
            print(f"{Fore.RED}[ERROR] Get media ID failed: {e}")
            return None
    
    def like_post(self, media_id: str) -> bool:
        """Like a post by media ID"""
        try:
            url = f"https://www.instagram.com/api/v1/web/media/{media_id}/like/"
            
            headers = self._get_headers({
                'Content-Type': 'application/x-www-form-urlencoded',
                'Referer': f"https://www.instagram.com/p/C{media_id}/",
                'X-IG-App-ID': '936619743392459'
            })
            
            response = self.session.post(url, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                return result.get('status') == 'ok'
            
            return False
            
        except Exception as e:
            print(f"{Fore.RED}[ERROR] Like failed: {e}")
            return False
    
    def follow_user(self, user_id: str) -> bool:
        """Follow a user by ID"""
        try:
            url = f"https://www.instagram.com/api/v1/web/friendships/{user_id}/follow/"
            
            response = self.session.post(url, headers=self._get_headers())
            
            if response.status_code == 200:
                result = response.json()
                return result.get('status') == 'ok'
            
            return False
            
        except Exception as e:
            return False
    
    def get_user_id(self, username: str) -> Optional[str]:
        """Get user ID from username"""
        try:
            url = f"https://www.instagram.com/api/v1/web/users/web_profile_info/?username={username}"
            response = self.session.get(url, headers=self._get_headers())
            
            if response.status_code == 200:
                data = response.json()
                return data.get('data', {}).get('user', {}).get('id')
            
            return None
            
        except Exception as e:
            return None
    
    def get_hashtag_feed(self, hashtag: str, count: int = 10) -> List[str]:
        """Get recent posts from hashtag"""
        try:
            url = f"https://www.instagram.com/api/v1/web/tags/{hashtag}/sections/"
            
            params = {
                'count': '12',
                'page': '0'
            }
            
            response = self.session.get(url, params=params, headers=self._get_headers())
            
            if response.status_code == 200:
                data = response.json()
                media_ids = []
                
                for section in data.get('sections', []):
                    for layout in section.get('layout_content', {}).get('medias', []):
                        if len(media_ids) >= count:
                            break
                        media = layout.get('media', {})
                        media_id = media.get('id')
                        if media_id:
                            media_ids.append(media_id)
                
                return media_ids
            
            return []
            
        except Exception as e:
            return []

# ==================== TIKTOK ENGINE ====================
class TikTokEngine:
    def __init__(self, proxy_manager: ProxyManager = None):
        self.session = requests.Session()
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
        ]
        self.proxy_manager = proxy_manager
        self.logged_in = False
        self.session_id = None
        
    def _get_headers(self, extra: Dict = None) -> Dict:
        """Generate headers for TikTok"""
        headers = {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin'
        }
        
        if extra:
            headers.update(extra)
            
        return headers
    
    def login(self, username: str, password: str) -> bool:
        """Login to TikTok (simplified)"""
        try:
            # TikTok requires mobile app or web login via OAuth
            # This is a simplified version - use API endpoints
            
            login_url = "https://www.tiktok.com/api/v1/auth/login/"
            
            data = {
                'username': username,
                'password': password,
                'service': 'https://www.tiktok.com/'
            }
            
            response = self.session.post(login_url, json=data, headers=self._get_headers({
                'Content-Type': 'application/json'
            }))
            
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'success':
                    self.logged_in = True
                    self.session_id = response.cookies.get('sessionid')
                    return True
            
            return False
            
        except Exception as e:
            print(f"{Fore.RED}[ERROR] TikTok login failed: {e}")
            return False
    
    def like_video(self, video_id: str) -> bool:
        """Like a TikTok video"""
        try:
            url = f"https://www.tiktok.com/api/v1/video/like/"
            
            data = {
                'video_id': video_id,
                'type': 'like'
            }
            
            response = self.session.post(url, json=data, headers=self._get_headers({
                'Content-Type': 'application/json',
                'Referer': f"https://www.tiktok.com/@user/video/{video_id}"
            }))
            
            if response.status_code == 200:
                result = response.json()
                return result.get('status') == 'success'
            
            return False
            
        except Exception as e:
            return False
    
    def get_video_id(self, video_url: str) -> Optional[str]:
        """Extract video ID from URL"""
        try:
            # Parse video URL
            if '/video/' in video_url:
                video_id = video_url.split('/video/')[1].split('?')[0]
                return video_id
            elif '/@' in video_url:
                # Get from API
                response = self.session.get(video_url, headers=self._get_headers())
                if response.status_code == 200:
                    # Extract from page
                    match = re.search(r'"videoId":"(\d+)"', response.text)
                    if match:
                        return match.group(1)
            
            return None
            
        except Exception as e:
            return None
    
    def get_hashtag_feed(self, hashtag: str, count: int = 10) -> List[str]:
        """Get recent videos from hashtag"""
        try:
            url = f"https://www.tiktok.com/api/v1/hashtag/feed/"
            
            params = {
                'challengeID': hashtag,
                'count': count
            }
            
            response = self.session.get(url, params=params, headers=self._get_headers())
            
            if response.status_code == 200:
                data = response.json()
                video_ids = []
                
                for item in data.get('items', []):
                    video_id = item.get('id')
                    if video_id:
                        video_ids.append(video_id)
                
                return video_ids
            
            return []
            
        except Exception as e:
            return []

# ==================== DEPARX MAIN CLASS ====================
class DeparxAutoLike:
    def __init__(self):
        self.proxy_manager = ProxyManager()
        self.account_manager = AccountManager()
        self.ig_engine = None
        self.tt_engine = None
        self.stats = {
            'total_likes': 0,
            'success_likes': 0,
            'failed_likes': 0,
            'start_time': None,
            'last_action': None
        }
        self.running = True
        self.config = {}
        
    def load_config(self, file_path: str = "config.json"):
        """Load configuration from JSON"""
        default_config = {
            'platform': 'instagram',  # instagram or tiktok
            'target_type': 'hashtag',  # hashtag, username, explore, custom
            'target_value': 'fyp',  # hashtag name or username
            'like_count': 50,  # Total likes per run
            'min_delay': 2,  # Minimum delay between likes (seconds)
            'max_delay': 8,  # Maximum delay between likes (seconds)
            'enable_proxy': False,
            'proxy_file': 'proxies.txt',
            'account_file': 'accounts.txt',
            'randomize_order': True,
            'max_per_minute': 20,
            'like_on_follow': False,
            'skip_duplicates': True
        }
        
        try:
            with open(file_path, 'r') as f:
                self.config = json.load(f)
                print(f"{Fore.GREEN}[✓] Config loaded from {file_path}")
        except:
            self.config = default_config
            with open(file_path, 'w') as f:
                json.dump(default_config, f, indent=4)
            print(f"{Fore.YELLOW}[!] Default config created: {file_path}")
        
        return self.config
    
    def initialize(self):
        """Initialize engines and load resources"""
        print(f"{Fore.CYAN}[*] Initializing DEPARX Auto Like...")
        
        # Load accounts
        account_count = self.account_manager.load_accounts(self.config.get('account_file', 'accounts.txt'))
        print(f"{Fore.GREEN}[✓] Loaded {account_count} accounts")
        
        # Load proxies
        if self.config.get('enable_proxy'):
            proxy_count = self.proxy_manager.load_proxies(self.config.get('proxy_file', 'proxies.txt'))
            print(f"{Fore.GREEN}[✓] Loaded {proxy_count} proxies")
        else:
            print(f"{Fore.YELLOW}[!] Proxy disabled")
        
        # Initialize engines based on platform
        platform = self.config.get('platform', 'instagram')
        
        if platform == 'instagram':
            self.ig_engine = InstagramEngine(self.proxy_manager if self.config.get('enable_proxy') else None)
        elif platform == 'tiktok':
            self.tt_engine = TikTokEngine(self.proxy_manager if self.config.get('enable_proxy') else None)
        
        print(f"{Fore.GREEN}[✓] Engine initialized for {platform}")
        return True
    
    def login_account(self, account: Dict) -> bool:
        """Login using account credentials"""
        platform = self.config.get('platform', 'instagram')
        
        if platform == 'instagram':
            return self.ig_engine.login(account['username'], account['password'])
        elif platform == 'tiktok':
            return self.tt_engine.login(account['username'], account['password'])
        return False
    
    def get_targets(self) -> List[str]:
        """Get targets based on configuration"""
        target_type = self.config.get('target_type')
        target_value = self.config.get('target_value')
        platform = self.config.get('platform', 'instagram')
        count = self.config.get('like_count', 50)
        
        if platform == 'instagram':
            engine = self.ig_engine
            
            if target_type == 'hashtag':
                return engine.get_hashtag_feed(target_value, count)
            elif target_type == 'username':
                user_id = engine.get_user_id(target_value)
                if user_id:
                    # Get user's recent posts
                    # Simplified - return user's feed
                    return []
            elif target_type == 'explore':
                # Get explore feed
                return []
            elif target_type == 'custom':
                # Load custom URLs from file
                try:
                    with open('targets.txt', 'r') as f:
                        targets = [line.strip() for line in f if line.strip()]
                    media_ids = []
                    for url in targets:
                        media_id = engine.get_media_id(url)
                        if media_id:
                            media_ids.append(media_id)
                    return media_ids
                except:
                    return []
        
        elif platform == 'tiktok':
            engine = self.tt_engine
            
            if target_type == 'hashtag':
                return engine.get_hashtag_feed(target_value, count)
            elif target_type == 'custom':
                try:
                    with open('targets.txt', 'r') as f:
                        targets = [line.strip() for line in f if line.strip()]
                    video_ids = []
                    for url in targets:
                        video_id = engine.get_video_id(url)
                        if video_id:
                            video_ids.append(video_id)
                    return video_ids
                except:
                    return []
        
        return []
    
    def like_target(self, target_id: str) -> bool:
        """Like a single target"""
        platform = self.config.get('platform', 'instagram')
        
        if platform == 'instagram':
            return self.ig_engine.like_post(target_id)
        elif platform == 'tiktok':
            return self.tt_engine.like_video(target_id)
        return False
    
    def run(self):
        """Main execution loop"""
        print(BANNER)
        print(f"{Fore.CYAN}[*] DEPARX Auto Like v{VERSION}")
        print(f"{Fore.CYAN}[*] Developer: {DEVELOPER}")
        print(f"{Fore.YELLOW}[*] Platform: {self.config.get('platform', 'instagram').upper()}")
        print(f"{Fore.YELLOW}[*] Target: {self.config.get('target_type')} → {self.config.get('target_value')}")
        print(f"{Fore.CYAN}[*] Starting auto like...\n")
        
        # Load config
        self.load_config()
        
        # Initialize
        if not self.initialize():
            print(f"{Fore.RED}[!] Initialization failed")
            return
        
        # Get account
        account = self.account_manager.get_next_account()
        if not account:
            print(f"{Fore.RED}[!] No accounts found")
            return
        
        # Login
        print(f"{Fore.CYAN}[*] Logging in as {account['username']}...")
        if not self.login_account(account):
            print(f"{Fore.RED}[!] Login failed")
            return
        print(f"{Fore.GREEN}[✓] Login successful")
        
        # Get targets
        print(f"{Fore.CYAN}[*] Fetching targets...")
        targets = self.get_targets()
        
        if not targets:
            print(f"{Fore.RED}[!] No targets found")
            return
        
        print(f"{Fore.GREEN}[✓] Found {len(targets)} targets")
        
        # Randomize order if enabled
        if self.config.get('randomize_order'):
            random.shuffle(targets)
        
        # Process each target
        self.stats['start_time'] = datetime.now()
        total_targets = min(len(targets), self.config.get('like_count', 50))
        
        print(f"{Fore.CYAN}[*] Starting like process...\n")
        
        for idx, target_id in enumerate(targets[:total_targets], 1):
            if not self.running:
                break
            
            try:
                # Like target
                success = self.like_target(target_id)
                self.stats['total_likes'] += 1
                
                if success:
                    self.stats['success_likes'] += 1
                    status = f"{Fore.GREEN}[✓] Like #{idx}"
                else:
                    self.stats['failed_likes'] += 1
                    status = f"{Fore.RED}[✗] Like #{idx}"
                
                # Update stats
                self.stats['last_action'] = datetime.now()
                
                # Print progress
                progress = f"{status} {Fore.WHITE}Total: {self.stats['total_likes']} | Success: {self.stats['success_likes']} | Failed: {self.stats['failed_likes']}"
                print(progress)
                
                # Random delay
                if idx < total_targets:
                    delay = random.uniform(
                        self.config.get('min_delay', 2),
                        self.config.get('max_delay', 8)
                    )
                    time.sleep(delay)
                    
            except Exception as e:
                print(f"{Fore.RED}[!] Error: {e}")
                time.sleep(5)
        
        # Print final stats
        self.print_stats()
    
    def print_stats(self):
        """Print execution statistics"""
        duration = datetime.now() - self.stats['start_time']
        success_rate = (self.stats['success_likes'] / max(1, self.stats['total_likes'])) * 100
        
        print(f"\n{Fore.CYAN}═══════════════════════════════════════════════")
        print(f"{Fore.GREEN}  DEPARX — Auto Like Statistics")
        print(f"{Fore.CYAN}═══════════════════════════════════════════════")
        print(f"{Fore.WHITE}  Total Likes      : {Fore.YELLOW}{self.stats['total_likes']}")
        print(f"{Fore.WHITE}  Successful       : {Fore.GREEN}{self.stats['success_likes']}")
        print(f"{Fore.WHITE}  Failed           : {Fore.RED}{self.stats['failed_likes']}")
        print(f"{Fore.WHITE}  Success Rate     : {Fore.CYAN}{success_rate:.1f}%")
        print(f"{Fore.WHITE}  Duration         : {Fore.YELLOW}{duration}")
        print(f"{Fore.CYAN}═══════════════════════════════════════════════")
        print(f"{Fore.GREEN}  Developed by: {DEVELOPER}")
        print(f"{Fore.CYAN}═══════════════════════════════════════════════\n")

# ==================== MENU SYSTEM ====================
def menu():
    print(BANNER)
    
    while True:
        print(f"\n{Fore.CYAN}┌─────────────────────────────────────────┐")
        print(f"{Fore.CYAN}│  DEPARX AUTO LIKE — MAIN MENU          │")
        print(f"{Fore.CYAN}├─────────────────────────────────────────┤")
        print(f"{Fore.GREEN}│  1. {Fore.WHITE}Start Auto Like")
        print(f"{Fore.GREEN}│  2. {Fore.WHITE}Configure Settings")
        print(f"{Fore.GREEN}│  3. {Fore.WHITE}Manage Accounts")
        print(f"{Fore.GREEN}│  4. {Fore.WHITE}Manage Proxies")
        print(f"{Fore.GREEN}│  5. {Fore.WHITE}Generate Accounts")
        print(f"{Fore.GREEN}│  6. {Fore.WHITE}Statistics")
        print(f"{Fore.GREEN}│  7. {Fore.WHITE}About")
        print(f"{Fore.GREEN}│  0. {Fore.RED}Exit")
        print(f"{Fore.CYAN}└─────────────────────────────────────────┘")
        
        choice = input(f"{Fore.YELLOW}\n[>] Choose option: ").strip()
        
        if choice == '1':
            deparx = DeparxAutoLike()
            deparx.load_config()
            deparx.run()
            
        elif choice == '2':
            configure_settings()
            
        elif choice == '3':
            manage_accounts()
            
        elif choice == '4':
            manage_proxies()
            
        elif choice == '5':
            generate_accounts()
            
        elif choice == '6':
            show_stats()
            
        elif choice == '7':
            about()
            
        elif choice == '0':
            print(f"\n{Fore.GREEN}[*] Thanks for using DEPARX!")
            print(f"{Fore.CYAN}[*] Developed by: {DEVELOPER}")
            sys.exit()
        else:
            print(f"{Fore.RED}[!] Invalid option")

def configure_settings():
    """Configure DEPARX settings"""
    print(f"\n{Fore.CYAN}┌─────────────────────────────────────────┐")
    print(f"{Fore.CYAN}│  CONFIGURE SETTINGS                    │")
    print(f"{Fore.CYAN}└─────────────────────────────────────────┘\n")
    
    config_file = 'config.json'
    
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
    except:
        config = {}
    
    # Platform
    print(f"{Fore.YELLOW}Platform:")
    print(f"  1. {Fore.WHITE}Instagram {Fore.GREEN}(current: {config.get('platform', 'instagram')})")
    print(f"  2. {Fore.WHITE}TikTok {Fore.GREEN}(current: {config.get('platform', 'instagram')})")
    plat_choice = input(f"{Fore.WHITE}Choose platform (1-2): ").strip()
    if plat_choice == '1':
        config['platform'] = 'instagram'
    elif plat_choice == '2':
        config['platform'] = 'tiktok'
    
    # Target Type
    print(f"\n{Fore.YELLOW}Target Type:")
    print(f"  1. Hashtag")
    print(f"  2. Username")
    print(f"  3. Custom (from targets.txt)")
    target_choice = input(f"{Fore.WHITE}Choose (1-3): ").strip()
    if target_choice == '1':
        config['target_type'] = 'hashtag'
        config['target_value'] = input(f"{Fore.WHITE}Hashtag (without #): ").strip()
    elif target_choice == '2':
        config['target_type'] = 'username'
        config['target_value'] = input(f"{Fore.WHITE}Username: ").strip()
    elif target_choice == '3':
        config['target_type'] = 'custom'
        config['target_value'] = 'targets.txt'
    
    # Like Count
    config['like_count'] = int(input(f"{Fore.WHITE}Number of likes: ") or "50")
    
    # Delays
    config['min_delay'] = float(input(f"{Fore.WHITE}Min delay (seconds): ") or "2")
    config['max_delay'] = float(input(f"{Fore.WHITE}Max delay (seconds): ") or "8")
    
    # Proxy
    proxy_choice = input(f"{Fore.WHITE}Enable proxy? (y/n): ").strip().lower()
    config['enable_proxy'] = proxy_choice == 'y'
    
    # Save
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=4)
    
    print(f"\n{Fore.GREEN}[✓] Settings saved to {config_file}")
    input(f"\n{Fore.YELLOW}Press Enter to continue...")

def manage_accounts():
    """Manage accounts list"""
    print(f"\n{Fore.CYAN}┌─────────────────────────────────────────┐")
    print(f"{Fore.CYAN}│  MANAGE ACCOUNTS                      │")
    print(f"{Fore.CYAN}└─────────────────────────────────────────┘\n")
    
    try:
        with open('accounts.txt', 'r') as f:
            accounts = [line.strip() for line in f if line.strip()]
    except:
        accounts = []
    
    print(f"{Fore.WHITE}Total accounts: {Fore.GREEN}{len(accounts)}")
    
    for idx, acc in enumerate(accounts, 1):
        print(f"  {idx}. {Fore.CYAN}{acc}")
    
    print(f"\n{Fore.YELLOW}Options:")
    print(f"  1. Add account")
    print(f"  2. Remove account")
    print(f"  3. Clear all")
    print(f"  4. Back")
    
    choice = input(f"{Fore.WHITE}Choose: ").strip()
    
    if choice == '1':
        new_acc = input(f"{Fore.WHITE}Enter username:password: ").strip()
        if ':' in new_acc:
            with open('accounts.txt', 'a') as f:
                f.write(f"{new_acc}\n")
            print(f"{Fore.GREEN}[✓] Account added")
    
    elif choice == '2':
        idx = int(input(f"{Fore.WHITE}Account number to remove: ").strip())
        if 1 <= idx <= len(accounts):
            del accounts[idx-1]
            with open('accounts.txt', 'w') as f:
                f.write('\n'.join(accounts))
            print(f"{Fore.GREEN}[✓] Account removed")
    
    elif choice == '3':
        confirm = input(f"{Fore.RED}Clear all accounts? (y/n): ").strip().lower()
        if confirm == 'y':
            with open('accounts.txt', 'w') as f:
                f.write('')
            print(f"{Fore.GREEN}[✓] All accounts cleared")
    
    input(f"\n{Fore.YELLOW}Press Enter to continue...")

def manage_proxies():
    """Manage proxy list"""
    print(f"\n{Fore.CYAN}┌─────────────────────────────────────────┐")
    print(f"{Fore.CYAN}│  MANAGE PROXIES                       │")
    print(f"{Fore.CYAN}└─────────────────────────────────────────┘\n")
    
    try:
        with open('proxies.txt', 'r') as f:
            proxies = [line.strip() for line in f if line.strip()]
    except:
        proxies = []
    
    print(f"{Fore.WHITE}Total proxies: {Fore.GREEN}{len(proxies)}")
    
    for idx, proxy in enumerate(proxies[:20], 1):
        print(f"  {idx}. {Fore.CYAN}{proxy}")
    
    if len(proxies) > 20:
        print(f"  ... and {len(proxies)-20} more")
    
    print(f"\n{Fore.YELLOW}Options:")
    print(f"  1. Add proxy")
    print(f"  2. Remove proxy")
    print(f"  3. Clear all")
    print(f"  4. Back")
    
    choice = input(f"{Fore.WHITE}Choose: ").strip()
    
    if choice == '1':
        new_proxy = input(f"{Fore.WHITE}Enter proxy (host:port or user:pass@host:port): ").strip()
        if new_proxy:
            with open('proxies.txt', 'a') as f:
                f.write(f"{new_proxy}\n")
            print(f"{Fore.GREEN}[✓] Proxy added")
    
    elif choice == '2':
        idx = int(input(f"{Fore.WHITE}Proxy number to remove: ").strip())
        if 1 <= idx <= len(proxies):
            del proxies[idx-1]
            with open('proxies.txt', 'w') as f:
                f.write('\n'.join(proxies))
            print(f"{Fore.GREEN}[✓] Proxy removed")
    
    input(f"\n{Fore.YELLOW}Press Enter to continue...")

def generate_accounts():
    """Generate fake accounts"""
    print(f"\n{Fore.CYAN}┌─────────────────────────────────────────┐")
    print(f"{Fore.CYAN}│  GENERATE ACCOUNTS                    │")
    print(f"{Fore.CYAN}└─────────────────────────────────────────┘\n")
    
    count = int(input(f"{Fore.WHITE}Number of accounts to generate: ").strip() or "10")
    
    domains = ['gmail.com', 'yahoo.com', 'outlook.com', 'protonmail.com']
    names = ['jason', 'alex', 'mary', 'john', 'lisa', 'eric', 'anna', 'david', 'emma', 'mike']
    surnames = ['smith', 'johnson', 'williams', 'brown', 'jones', 'garcia', 'miller', 'davis']
    
    generated = []
    for _ in range(count):
        username = random.choice(names) + str(random.randint(1000, 9999))
        email = f"{username}@{random.choice(domains)}"
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
        generated.append(f"{username}:{password}")
    
    with open('accounts.txt', 'a') as f:
        f.write('\n'.join(generated) + '\n')
    
    print(f"{Fore.GREEN}[✓] Generated {count} accounts")
    print(f"{Fore.YELLOW}First 5 accounts:")
    for acc in generated[:5]:
        print(f"  {Fore.CYAN}{acc}")
    
    input(f"\n{Fore.YELLOW}Press Enter to continue...")

def show_stats():
    """Show statistics"""
    print(f"\n{Fore.CYAN}┌─────────────────────────────────────────┐")
    print(f"{Fore.CYAN}│  DEPARX STATISTICS                    │")
    print(f"{Fore.CYAN}└─────────────────────────────────────────┘\n")
    
    try:
        with open('stats.log', 'r') as f:
            stats = json.load(f)
    except:
        stats = {'total_likes': 0, 'runs': 0}
    
    print(f"{Fore.WHITE}Total Likes: {Fore.GREEN}{stats.get('total_likes', 0)}")
    print(f"{Fore.WHITE}Total Runs: {Fore.CYAN}{stats.get('runs', 0)}")
    print(f"{Fore.WHITE}Last Run: {Fore.YELLOW}{stats.get('last_run', 'Never')}")
    
    input(f"\n{Fore.YELLOW}Press Enter to continue...")

def about():
    """About DEPARX"""
    print(f"\n{Fore.CYAN}┌─────────────────────────────────────────┐")
    print(f"{Fore.CYAN}│  ABOUT DEPARX                         │")
    print(f"{Fore.CYAN}└─────────────────────────────────────────┘\n")
    
    print(f"{Fore.GREEN}Name: {Fore.WHITE}DEPARX Auto Like Tools")
    print(f"{Fore.GREEN}Version: {Fore.WHITE}{VERSION}")
    print(f"{Fore.GREEN}Developer: {Fore.WHITE}{DEVELOPER}")
    print(f"{Fore.GREEN}TikTok: {Fore.WHITE}@promptbyzaax__")
    print(f"{Fore.GREEN}Engine: {Fore.WHITE}FOLYST Neural Freedom Protocol")
    print(f"\n{Fore.YELLOW}Description:")
    print(f"{Fore.WHITE}  DEPARX is an advanced auto-like tool for")
    print(f"{Fore.WHITE}  Instagram and TikTok with multi-account")
    print(f"{Fore.WHITE}  support, proxy rotation, and anti-block")
    print(f"{Fore.WHITE}  mechanisms.")
    
    input(f"\n{Fore.YELLOW}Press Enter to continue...")

# ==================== MAIN ====================
if __name__ == '__main__':
    try:
        menu()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.RED}[!] Interrupted")
        print(f"{Fore.CYAN}[*] Thanks for using DEPARX!")
        print(f"{Fore.CYAN}[*] Developed by: {DEVELOPER}")
        sys.exit()
