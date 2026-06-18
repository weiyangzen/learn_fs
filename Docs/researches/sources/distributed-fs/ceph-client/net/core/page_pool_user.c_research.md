<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/page_pool_user.c -->
# sources/distributed-fs/ceph-client/net/core/page_pool_user.c

## Purpose
User-visible registry and generic-netlink reporting for page pools. It assigns stable IDs, links pools to netdevices, reports inflight and stats data, sends page-pool multicast notifications, and preserves user visibility when devices unregister.

## APIs, Types, and Functions
Externally used functions are `page_pool_list()`, `page_pool_detached()`, `page_pool_unlist()`, and `page_pool_check_memory_provider()`. Netlink handlers include `netdev_nl_page_pool_get_doit/dumpit()` and `netdev_nl_page_pool_stats_get_doit/dumpit()`. Fill helpers are `page_pool_nl_fill()` and `page_pool_nl_stats_fill()`.

## Control Flow, State, and Persistence
Global `page_pools` xarray maps IDs to pools and `page_pools_lock` protects the xarray, per-device `page_pools` hlists, pool user fields, NAPI pointer visibility, and `slow.netdev`. Listing allocates a cyclic 32-bit ID, initializes the hlist node, links to the creating netdev when present, and sends add notifications. GET validates namespace and visibility before serializing ID, ifindex, NAPI ID, inflight page/memory counts, detach time, and provider-specific attributes. Dumps walk netdevs and their pool hlists under RTNL plus `page_pools_lock`. On netdev unregister, pools move to loopback as orphaned visible pools; loopback unregister wipes them invisible with poisoned netdev pointers.

## Dependencies and Integration
Depends on page-pool core stats/inflight APIs, generated netdev generic-netlink attributes, network namespaces, RTNL, netdevice notifier chain, memory-provider `nl_fill()`, and loopback device lifetime.

## Risks and Test Signals
Risks include lock ordering with RTNL, userspace-visible orphan semantics, stale provider binding validation in `page_pool_check_memory_provider()`, and stats behavior when `CONFIG_PAGE_POOL_STATS` is off. Test signals are ID allocation/list/unlist, get and dump namespace filtering, add/change/delete notifications, orphan move to loopback on device unregister, wipe on loopback unregister, stats `-EOPNOTSUPP` without stats config, and provider lookup matching queue index plus binding pointer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/page_pool_user.c -->
