# sources/distributed-fs/ceph-client/drivers/net/netdevsim/hwstats.c

Purpose: simulates hardware offload extended statistics for selected netdevices, currently L3 stats, with debugfs control over tracked ifindexes and enable failure.

Important APIs/types/functions: `struct nsim_dev_hwstats` owns debugfs, an L3 tracked-device list, a netdevice notifier, lock, and periodic traffic work. `struct nsim_dev_hwstats_netdev` stores a referenced netdev, accumulated `rtnl_hw_stats64`, and flags. `nsim_dev_hwstats_init()`/`exit()` manage the subsystem. `nsim_dev_hwstats_event_off_xstats()` handles enable, disable, report-used, and report-delta notifications.

Control flow: init registers a netdevice notifier, creates `hwstats/l3/{enable_ifindex,disable_ifindex,fail_next_enable}`, and starts delayed traffic work. Enabling by ifindex grabs a netdev reference and adds an entry; if kernel offload stats are already enabled, it enables and notifies immediately. The work bumps counters every 100 ms for enabled entries. Disable pushes pending deltas when needed, notifies, removes the entry, and releases the netdev.

State and persistence: tracked devices are held in an in-memory list protected by `hwsdev_list_lock`. Stats are accumulated until reported as a delta or disabled, then reset. `fail_enable` causes exactly one enable callback to fail and is then cleared.

Dependencies and integration: uses netdevice notifier events, `netdev_offload_xstats_*` helpers, RTNL, debugfs auxiliary file data, delayed work, and `nsim_dev_net()`.

Risks: lock ordering crosses RTNL and the hwstats mutex in debugfs paths; notifier paths take only the mutex. If a tracked ifindex unregisters, the notifier must remove it before stale netdev use. The synthetic traffic schedule continues until explicit exit.

Test signals: enable an ifindex through debugfs, request offload xstats used/delta, verify periodic increments and reset-after-delta, inject `fail_next_enable`, unregister tracked devices, and confirm delayed work cancellation on module/device removal.
