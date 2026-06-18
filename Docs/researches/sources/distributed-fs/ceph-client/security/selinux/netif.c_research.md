<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/netif.c -->
# sources/distributed-fs/ceph-client/security/selinux/netif.c

## Purpose
Maintains a fast SELinux SID cache for network interfaces because `net_device` does not carry SELinux security state directly. It maps `(network namespace, ifindex)` to interface SID and invalidates entries when devices go down.

## Important APIs, Types, and Functions
The public API is `sel_netif_sid()` and `sel_netif_flush()`, with init through `sel_netif_init()`. Core helpers are `sel_netif_hashfn()`, `sel_netif_find()`, `sel_netif_insert()`, `sel_netif_destroy()`, `sel_netif_sid_slow()`, `sel_netif_kill()`, and `sel_netif_netdev_notifier_handler()`. `struct sel_netif` wraps `struct netif_security_struct` with list and RCU fields.

## Control Flow
Fast lookup runs under `rcu_read_lock()` and returns a cached SID when present. Misses call `sel_netif_sid_slow()`, which gets the device by ifindex, locks the table, rechecks the cache, calls `security_netif_sid(dev->name, sid)`, and inserts a new cache record if memory and global table limits allow. A `NETDEV_DOWN` notifier removes the corresponding entry.

## State and Persistence
State is a 64-bucket RCU hash table, global `sel_netif_total`, and `sel_netif_lock`. The cache persists across packets until device-down invalidation, explicit flush, policy reload flush from other code, or the hard `SEL_NETIF_HASH_MAX` limit preventing more inserts.

## Dependencies and Integration Points
Depends on netdevice lookup/lifetime, network namespaces, SELinux policy lookup via `security_netif_sid()`, object security structures, and the netdevice notifier chain. Packet path hooks use this cache when checking interface labels.

## Risks
`sel_netif_flush()` iterates while deleting entries; list-safe iteration would be less fragile if multiple entries exist in a bucket. The hash combines namespace pointer and ifindex, but comments indicate container labeling is not fully supported. Cache insert failures are intentionally nonfatal, so repeated misses can hurt performance.

## Test Signals
Test lookup hit/miss behavior, policy-defined interface labels, invalid ifindex errors, cache flush after policy reload, `NETDEV_DOWN` invalidation, table-full behavior, and concurrent lookups/removals under RCU with lockdep/KCSAN enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/netif.c -->
