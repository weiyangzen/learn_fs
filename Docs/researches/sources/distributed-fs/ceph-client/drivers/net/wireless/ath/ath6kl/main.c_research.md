<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/main.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/main.c

## Purpose
`main.c` is the driver’s runtime glue between firmware WMI events, cfg80211 notifications, Linux netdev operations, AP station state, multicast filters, target statistics, and diagnostic access. It does not probe hardware; it manages per-VIF behavior after core initialization.

## Important APIs, Types, And Functions
Station helpers `ath6kl_find_sta()`, `ath6kl_find_sta_by_aid()`, `ath6kl_add_new_sta()`, `ath6kl_sta_cleanup()`, and `ath6kl_remove_sta()` manage `ar->sta_list`, AP stats, WPA/WAPI IEs, power-save queues, and aggregation connection state. Cookie helpers `ath6kl_cookie_init()`, `ath6kl_alloc_cookie()`, `ath6kl_free_cookie()`, and `ath6kl_cookie_cleanup()` provide the TX context pool used by `txrx.c`.

Diagnostic functions `ath6kl_diag_read32()`, `ath6kl_diag_write32()`, `ath6kl_diag_read()`, and `ath6kl_diag_write()` wrap HIF diagnostic ops. `ath6kl_read_fwlogs()` walks the target debug log ring using host-interest addresses from `target.h`.

WMI event handlers include ready, connect, disconnect, scan complete, TKIP MIC error, target stats, wakeup, TX power, PS-Poll, and DTIM expiry processing. Netdev integration is via `ath6kl_open()`, `ath6kl_close()`, `ath6kl_set_features()`, `ath6kl_set_multicast_list()`, `ath6kl_netdev_ops`, and `init_netdev()`.

## Control Flow
Ready events populate MAC/version/capability state and wake startup waiters. Connect events notify cfg80211, update BSSID/channel, wake queues, set `CONNECTED`, reset aggregation, and adjust BSS filters. AP mode has separate BSS-start and station-association handlers that install delayed group keys, notify cfg80211 of new stations, and initialize per-station aggregation. Disconnect flow diverges by AP versus station mode: AP removes station state and cfg80211 station objects; station mode notifies cfg80211, resets aggregation, manages reconnect flags, stops queues, clears BSSID/channel, and flushes data TX.

Power-save events drive queued AP delivery: PS-Poll drains one management or data frame, DTIM expiry drains multicast PS queue, and PVB bits are updated through WMI. Multicast filter changes compare netdev multicast addresses against `vif->mc_filter`, issuing WMI add/delete commands.

## State And Persistence
All state is volatile kernel memory: station slots, AP stats, WEP/group keys stored on VIF/core structures, cookies, target stats accumulators, multicast filter list, connect flags, carrier/queue state, and firmware log snapshots. The file mutates `ar->state` indirectly only through netdev and WMI-facing behavior; persistent device configuration is pushed to firmware with WMI commands.

## Dependencies And Integration Points
Dependencies include cfg80211 notification APIs, netdev ops, WMI command/event structures, HIF diagnostic ops, target host-interest constants, aggregation helpers from `txrx.c`, and debugfw log plumbing. `init.c` waits for `ath6kl_ready_event()` effects; `txrx.c` consumes cookie and station helpers.

## Risks
Station cleanup assumes valid AID-derived array indexes; callers mostly validate AID but future paths must maintain this. AP power-save queueing and cfg80211 station notifications run across spinlocks and unlocked WMI calls; race regressions are plausible around disconnect, wake, DTIM, and removal. `ath6kl_set_features()` changes global `ar->rx_meta_ver` from per-netdev feature toggles, which matters in multi-VIF scenarios. Firmware log reading trusts target ring pointers but uses bounded loop count.

## Test Signals
Signals include cfg80211 connect/disconnect/new_sta/del_sta events, netdev carrier and queue transitions, multicast filter WMI command failures, target stats wakeups, TX power wakeups, AP max-client and ACL failure notifications, firmware log extraction, and checksum feature toggling. Stress tests should cover AP station churn, PS-Poll/DTIM delivery, multicast list changes while suspended or disconnected, and station-mode reconnect edge cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/main.c -->
