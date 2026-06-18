# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/p2p.c

## Purpose
`p2p.c` implements P2P listen/search discovery operations for 60 GHz social channel behavior. It configures firmware discovery state, coordinates scan/listen timers, reports remain-on-channel and scan completion to cfg80211, and stops radio operations during down/reset.

## Important APIs, Types, And Functions
`wil_p2p_is_social_scan()` identifies a social-channel scan. `wil_p2p_search()` configures P2P search, sets wildcard SSID and probe IEs, starts search, and arms the search timer. `wil_p2p_listen()` starts or delays remain-on-channel listen. `wil_p2p_stop_discovery()`, `wil_p2p_cancel_listen()`, `wil_p2p_listen_expired()`, `wil_p2p_search_expired()`, `wil_p2p_delayed_listen_work()`, and `wil_p2p_stop_radio_operations()` manage completion and cancellation.

## Control Flow
Search/listen operations serialize on `wil->mutex`. Listen checks for an in-progress scan under `vif_mutex`; if present, it records a pending listen and waits for delayed work. Actual start uses `wmi_p2p_cfg()`, `wmi_set_ssid()`, and either `wmi_start_listen()` or `wmi_start_search()`, then arms `discovery_timer`. Expiry work stops firmware discovery and reports cfg80211 completion. Cancellation validates the cookie, stops discovery, and sends remain-on-channel expired.

## State And Persistence
State lives in `vif->p2p`: `discovery_started`, `cookie`, `listen_chan`, `listen_duration`, `pending_listen_wdev`, timer, and work items. `wil->radio_wdev` is switched to the P2P wdev during main-MID radio operations and restored when complete.

## Dependencies And Integration Points
The file depends on WMI P2P/SSID/IE/discovery commands, cfg80211 scan and remain-on-channel APIs, timers/workqueues initialized by `netdev.c`, and scan abort/reset paths in `main.c`. It assumes lock ownership documented by `lockdep_assert_held()`.

## Risks
Search/listen and scan share VIF/radio state, so delayed listen and abort paths must avoid double completion. `wil_p2p_stop_radio_operations()` temporarily drops `vif_mutex` while stopping discovery, which requires callers to hold `wil->mutex`. Cookie mismatch and pending-listen cases need exact cfg80211 signaling to avoid userspace hangs.

## Test Signals
Run social-channel scans, listen during active scan, cancel listen with valid/invalid cookies, reset/down during P2P discovery, timer expiry for search and listen, WMI command failures, and radio_wdev restoration after every exit path.
