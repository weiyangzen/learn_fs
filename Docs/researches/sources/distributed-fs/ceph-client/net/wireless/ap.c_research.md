# sources/distributed-fs/ceph-client/net/wireless/ap.c

## Purpose
This file implements cfg80211 access point stop handling for AP and P2P GO interfaces, including multi-link stop support.

## Important APIs, types, and functions
`___cfg80211_stop_ap()` stops one link after validating driver support, interface type, and active beacon state. It calls `rdev_stop_ap()`, clears ownership and AP state, resets QoS map, optionally sends `nl80211_send_ap_stopped()`, schedules DFS channel updates, and queues disconnect work. `cfg80211_stop_ap()` is the public wrapper that stops either a specified link or all valid links.

## Control flow
For a specific link, the wrapper delegates directly. For all links, it iterates `for_each_valid_link()` and attempts each stop even if earlier links fail, preserving the last error. The internal helper returns `-EOPNOTSUPP` for missing ops or wrong iftype and `-ENOENT` when the link is not beaconing.

## State and persistence
AP state is in `wireless_dev`: `conn_owner_nlportid`, per-link `ap.beacon_interval`, per-link chandef, and shared AP SSID length. State is cleared only after the driver stop succeeds. There is no durable persistence.

## Dependencies and integration points
The file depends on cfg80211 core structures, nl80211 notifications, `rdev-ops.h`, QoS map operations, DFS scheduling, and global `cfg80211_disconnect_work`.

## Risks
Multi-link stop must not leave partially stopped state hidden from userspace. The helper clears shared `wdev->u.ap.ssid_len` on each successful link stop, which is correct for current semantics but should be reviewed for future per-link SSID state. DFS updates must happen after beaconing state changes.

## Test signals
Tests should cover stop without driver op, stop on non-AP iftypes, inactive link, successful single-link stop, all-links stop with mixed failures, nl80211 notification behavior, and DFS update scheduling.
