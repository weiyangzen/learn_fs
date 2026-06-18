# sources/distributed-fs/ceph-client/net/wireless/ibss.c

## Purpose
This file implements cfg80211 IBSS/ad-hoc join, joined notification, leave, cleanup, and WEXT compatibility operations.

## Important APIs, types, and functions
`__cfg80211_join_ibss()` validates state, derives default basic rates, stores cached WEP keys, records the chandef, and calls `rdev_join_ibss()`. `__cfg80211_ibss_joined()` updates the current BSS reference, uploads cached keys, and notifies nl80211/WEXT. `cfg80211_ibss_joined()` queues that event through the wdev event list. `cfg80211_clear_ibss()` releases keys, QoS map, default keys, BSS refs, SSID/chandef state, and schedules DFS update. `cfg80211_leave_ibss()` calls `rdev_leave_ibss()` and clears state.

WEXT helpers support automatic channel selection, frequency get/set, ESSID get/set, and AP/BSSID get/set.

## Control flow
Join rejects active CAC, already joined state, invalid cached keys, or missing driver support. If no basic rates were configured, it selects mandatory 11a rates for 5/6 GHz or 11b rates otherwise. On successful driver join, it copies SSID state. Joined events later resolve the BSS from scan cache and transfer the active BSS reference into `wdev->u.ibss.current_bss`.

Leave requires an active SSID, delegates to the driver, clears connection owner, and resets IBSS state. WEXT setters leave an existing IBSS before changing channel, SSID, or fixed BSSID, then attempt a new join if enough state and netdev running state are present.

## State and persistence
IBSS state lives in `wdev->u.ibss`, `wdev->connect_keys`, WEXT compatibility fields, and held BSS references. There is no durable persistence.

## Dependencies and integration points
The file depends on nl80211 notifications, WEXT compatibility when enabled, scan/BSS helpers, DFS scheduling, QoS map operations, and driver ops from `rdev-ops.h`.

## Risks
BSS reference ownership is critical during joined and clear paths. WEXT automatic channel selection must avoid disabled and NO_IR channels. Cached key memory contains sensitive material and must be freed with `kfree_sensitive()`. DFS updates must follow leave/clear.

## Test signals
Tests should cover join defaults by band, missing driver ops, CAC busy rejection, duplicate join, joined event without BSS, leave without connection, WEXT channel/SSID/BSSID changes, key cleanup, and BSS refcount balance.
