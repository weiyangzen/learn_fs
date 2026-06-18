# sources/distributed-fs/ceph-client/include/net/cfg80211-wext.h

## Purpose
This header declares transitional Wireless Extensions handlers implemented on top of cfg80211. It supports drivers that have not fully converted away from WEXT by exposing standard iw_handler-compatible callbacks for name, mode, scanning, range, RTS, fragmentation, and retry queries/settings.

## Important APIs, Types, And Constants
- `cfg80211_wext_giwname()` reports the wireless protocol/name.
- `cfg80211_wext_siwmode()` and `cfg80211_wext_giwmode()` set/get interface mode.
- `cfg80211_wext_siwscan()` and `cfg80211_wext_giwscan()` trigger and retrieve scans.
- `cfg80211_wext_giwrange()` reports supported ranges/capabilities.
- `cfg80211_wext_siwrts()`/`giwrts()` set/get RTS threshold.
- `cfg80211_wext_siwfrag()`/`giwfrag()` set/get fragmentation threshold.
- `cfg80211_wext_giwretry()` reports retry settings.
All functions use the WEXT callback signature: `struct net_device *`, `struct iw_request_info *`, `union iwreq_data *`, and extra buffer.

## Control Flow And State
Legacy WEXT ioctl dispatch invokes these handlers through a driver's iw_handler table. The handler translates WEXT requests into cfg80211 operations or cfg80211-maintained state, fills `iwreq_data` and optional extra buffers, and returns a Linux errno. Scan flow is asynchronous at the device layer: set-scan starts work, while get-scan serializes cached scan results.

## State And Persistence Behavior
The header stores no state. Mode, scan results, RTS/fragmentation thresholds, and retry data are held by cfg80211/wireless driver state. WEXT callers see a compatibility projection of that state.

## Dependencies And Integration Points
The header depends on netdevice, `linux/wireless.h`, and `net/iw_handler.h`. It integrates with cfg80211, legacy wireless ioctl handling, and partially converted wireless drivers.

## Risks
- WEXT and cfg80211 semantics do not always map one-to-one; translation can lose detail or expose stale cached scan results.
- Extra buffer sizing for scan/range results must be validated by implementation code to avoid truncation or overflow.
- These handlers are explicitly transitional, so new driver work should avoid expanding WEXT-only behavior.

## Test Signals
- Wireless compatibility tests should cover WEXT mode get/set, scan trigger/result retrieval, range reporting, RTS/fragmentation threshold set/get, retry reporting, and buffer-too-small behavior.
- Driver integration tests should confirm cfg80211-native state and WEXT views remain consistent.
