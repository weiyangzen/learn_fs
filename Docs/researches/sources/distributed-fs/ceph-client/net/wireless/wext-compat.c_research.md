# sources/distributed-fs/ceph-client/net/wireless/wext-compat.c

## Purpose
`wext-compat.c` implements cfg80211's Wireless Extensions compatibility layer. It translates legacy WEXT ioctl handlers into cfg80211/nl80211 state and driver operations so older userspace tools such as `iwconfig` can still interact with cfg80211-backed devices. The file is explicitly temporary compatibility code, but it remains broad: mode, range, frequency, RTS/fragment/retry, encryption, authentication, power, bitrate, statistics, AP/ESSID, and PMKSA handlers all live here.

## Important APIs And Functions
Public handlers include `cfg80211_wext_giwname`, `cfg80211_wext_siwmode`, `cfg80211_wext_giwmode`, `cfg80211_wext_giwrange`, `cfg80211_wext_freq`, `cfg80211_wext_siwrts`, `cfg80211_wext_giwrts`, `cfg80211_wext_siwfrag`, and `cfg80211_wext_giwfrag`.

Static WEXT handlers registered in `cfg80211_handlers[]` include retry, encode/encodeext, get encode, set/get frequency, set/get tx power, set/get auth, set/get power save, set/get rate, wireless stats, set/get AP, set/get ESSID, and PMKSA. The file exports `cfg80211_wext_handler`, an `iw_handler_def` used by wireless netdevices.

The central security translation helper is `cfg80211_set_encryption`. It allocates legacy WEXT key storage, validates interface type and MLO constraints, maps remove/add/default-key requests to `rdev_del_key`, `rdev_add_key`, `rdev_set_default_key`, and `rdev_set_default_mgmt_key`, stores pre-connect WEP keys, and triggers IBSS rejoin when privacy/default-key state changes.

Authentication helpers translate WEXT flags to cfg80211 connect parameters: `cfg80211_set_auth_alg`, `cfg80211_set_wpa_version`, `cfg80211_set_cipher_group`, `cfg80211_set_cipher_pairwise`, and `cfg80211_set_key_mgt`.

## Control Flow
Most handlers follow a common pattern:

1. Extract WEXT request data from `union iwreq_data`.
2. Resolve `wireless_dev` and `cfg80211_registered_device`.
3. Reject unsupported interface types, missing driver ops, unsupported MLO cases, or invalid WEXT flags.
4. Acquire the wiphy lock with `guard(wiphy)` or `scoped_guard(wiphy, ...)`.
5. Translate legacy WEXT encoding into cfg80211 structures.
6. Call cfg80211 core or rdev operation wrappers.
7. Update cached WEXT/cfg80211 state only when the driver call succeeds, rolling back where needed.

Mode setting maps `IW_MODE_INFRA`, `IW_MODE_ADHOC`, and `IW_MODE_MONITOR` to station, IBSS, and monitor iftypes, then calls `cfg80211_change_iface`. Range reporting fills `iw_range` from wiphy signal type, cipher suites, supported channels, retry/RTS/fragment limits, scan capability, and event capability.

Frequency handling delegates station and IBSS requests to managed/IBSS WEXT helpers declared in the header. Monitor and mesh paths parse WEXT frequency/channel encoding with `cfg80211_wext_freq`, resolve the channel, and call monitor or mesh channel setters.

Encryption handling supports old `SIOCSIWENCODE` WEP paths and `SIOCSIWENCODEEXT` WEP/TKIP/CCMP/AES-CMAC paths. It maps broadcast addresses to group keys, handles RX sequence presence, and relies on `cfg80211_validate_key_settings` for key policy. Authentication settings update cached `wdev->wext.connect` fields for later connection attempts.

The handler table maps standard WEXT ioctl numbers to these functions, while `cfg80211_wireless_stats` supplies `/proc/net/wireless` and `SIOCGIWSTATS` data by querying station info from the driver.

## State And Persistence Behavior
This file maintains compatibility state inside `wdev->wext`. It caches WEP keys in `wdev->wext.keys`, tracks `default_key` and `default_mgmt_key`, stores connection privacy/auth/cipher/AKM settings in `wdev->wext.connect`, and updates `wdev->ps`/`wdev->ps_timeout` after successful power-management changes. It also mutates wiphy-level RTS, fragmentation, retry, and rfkill state.

Pre-connect WEP key persistence is intentional: WEP keys can be configured before association and later uploaded when joining. Non-WEP keys are generally rejected before connection and not persisted in the WEXT cache. IBSS privacy changes can leave and rejoin the IBSS to reflect privacy-bit changes.

`cfg80211_wireless_stats` uses static `iw_statistics` and `station_info` storage because callers are under RTNL. It releases station-info dynamic content before returning.

## Dependencies And Integration Points
The file depends on legacy WEXT headers (`linux/wireless.h`, `net/iw_handler.h`, `net/cfg80211-wext.h`), cfg80211/nl80211 types, local `wext-compat.h`, `core.h`, and `rdev-ops.h`. It integrates with managed and IBSS compatibility helpers declared in `wext-compat.h`, scan/MLME WEXT helpers supplied elsewhere, rfkill, station statistics, and cfg80211 driver ops.

The exported `cfg80211_wext_handler` is the integration point consumed by cfg80211 netdevice setup. Legacy ioctl users enter cfg80211 through this table rather than through nl80211 netlink APIs.

## Risks And Edge Cases
WEXT is a lossy legacy API. Several modern capabilities are unsupported or rejected, notably valid-links/MLO in encryption, bitrate, stats, and many single-link assumptions. Station-only paths often rely on `links[0].client.current_bss`.

Security behavior is delicate. WEP pre-connect storage, AES-CMAC management key indexes, pairwise/group address rules, and IBSS RSN exceptions must remain aligned with `util.c` validation. `cfg80211_set_encryption` allocates key storage before some validation paths, which is intentional for later use but can leave allocated empty compatibility storage.

Power and rfkill behavior has side effects: disabling TX power maps to software rfkill and may schedule rfkill block work. RTS/fragment/retry setters optimistically update wiphy fields and roll back on driver errors.

Range and statistics reporting compress cfg80211 data into older WEXT fields. Signal conversion, quality scaling, channel count limits (`IW_MAX_FREQUENCIES`), and cipher capability bits can be approximate.

## Test Signals
Compatibility tests should exercise `iwconfig` mode/frequency/rate/txpower/rts/frag/retry/power paths against station, IBSS, monitor, and mesh interfaces. Encryption tests should cover WEP pre-connect add/get/remove/default-key behavior, TKIP/CCMP connected-only behavior, AES-CMAC management key indexes, pairwise address requirements, and IBSS rejoin on default-key privacy changes. Stats tests should validate MBM and unspecified signal mappings. Negative tests should cover missing driver ops, unsupported interface types, invalid WEXT flags, MLO devices, out-of-range frequencies, and channel lookup failures.
