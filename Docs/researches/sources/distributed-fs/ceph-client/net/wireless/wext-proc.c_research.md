# sources/distributed-fs/ceph-client/net/wireless/wext-proc.c

Purpose: exposes `/proc/net/wireless`, a seq_file view of Wireless Extensions statistics for each wireless-capable network device in a network namespace.

Important APIs/functions: `wext_proc_init()` creates the proc entry, `wext_proc_exit()` removes it, and seq callbacks `wireless_dev_seq_start/next/stop/show()` walk netdevices under RTNL. `wireless_seq_printf_stats()` formats `struct iw_statistics`.

Control flow: opening the proc file uses the net namespace embedded by `proc_create_net()`. The seq iterator locks RTNL, emits a fixed header at `SEQ_START_TOKEN`, then visits each netdev. For each device, it asks `get_wireless_stats()` for live stats; if unavailable but the device advertises wireless handlers or an `ieee80211_ptr`, it prints a zeroed row so wireless devices remain visible.

State and persistence: proc output is generated on demand. A successful live stats read clears `IW_QUAL_ALL_UPDATED`; the static null stats row is never used to mutate driver state.

Dependencies and integration: depends on procfs, seq_file, per-net proc directories, netdevice iteration, and the WEXT stats helper in `wext-core.c`.

Risks and test signals: this is mostly diagnostic, but locking and side effects matter. Tests should validate namespace-specific `/proc/net/wireless`, header formatting, wireless devices with missing stats, clearing updated flags, RTNL-protected device removal during reads, and builds without legacy WEXT or cfg80211 stats providers.
