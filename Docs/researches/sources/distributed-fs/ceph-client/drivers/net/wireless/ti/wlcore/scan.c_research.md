# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/scan.c

## Purpose
`scan.c` provides common scan bookkeeping and channel/SSID preparation for wlcore. Chip-specific operations still perform the actual firmware scan start/stop, while this file translates cfg80211 scan requests into wlcore channel structures, schedules completion timeout handling, and exposes scheduled-scan helper routines.

## Important APIs, Types, and Functions
`wlcore_scan()` starts a regular hardware scan after validating state, copying an optional SSID, setting `wl->scan_wlvif`/`wl->scan.req`, assuming failure until completion, scheduling `scan_complete_work`, and calling `wl->ops->scan_start()`. `wl1271_scan_complete_work()` is the timeout/completion worker that idles scan state, restores AP probe request templates for associated STA mode, queues recovery on failed scans, refreshes regdomain config, and calls `ieee80211_scan_completed()`. `wlcore_set_scan_chan_params()` and private `wlcore_scan_get_channels()` build active/passive/DFS channel arrays and dwell times for search or scheduled scan. `wlcore_scan_sched_scan_ssid_list()` emits the firmware SSID filter command for scheduled scan. `wlcore_scan_sched_scan_results()` notifies mac80211 of periodic scan results.

## Control Flow
Channel preparation runs in ordered passes: 2.4 GHz passive, 2.4 GHz active, 5 GHz passive, 5 GHz DFS, 5 GHz active, with 802.11j currently disabled. Passive-active channels 12-14 can be treated as DFS-like entries when no forced passive scan is required. Dwell times differ for foreground search scans versus periodic scans and are converted from microseconds to milliseconds for firmware structures.

## State and Persistence Behavior
Scan state is in `wl->scan`: state enum, requested SSID, scanned channel bitmask, failure flag, and cfg80211 request pointer. `wl->scan_wlvif` tracks the owning vif. Scheduled scan owner is handled in `main.c` through `wl->sched_vif`. No state persists across module reload; scan completion clears transient fields.

## Dependencies and Integration Points
Dependencies include Linux `ieee80211_channel`, cfg80211 scan/sched-scan requests, runtime PM in completion work, `cmd.h`, `acx.h`, `tx.h`, and chip-specific `wl->ops` scan callbacks. `main.c` wraps these helpers in mac80211 callbacks and handles cancel paths.

## Risks and Test Signals
Risks include stale `scan_wlvif` if an interface is removed mid-scan, timeout-driven recovery after firmware scan failure, dwell-time conversion mistakes, off-by-one channel packing for passive/DFS channels, and strict SSID filter validation for scheduled scan hidden SSIDs. Tests should cover normal scan, cancel scan, timeout failure, associated STA scan template restoration, scheduled scan with match sets, hidden SSIDs, passive-only scans, DFS channel inclusion, and regulatory refresh after scan.
