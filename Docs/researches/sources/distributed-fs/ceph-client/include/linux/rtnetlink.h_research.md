# sources/distributed-fs/ceph-client/include/linux/rtnetlink.h

## Purpose
`rtnetlink.h` declares rtnetlink notification helpers and the RTNL locking interface used to serialize network configuration changes.

## Important APIs, types, and functions
Important functions include `rtnetlink_send()`, `rtnetlink_maybe_send()`, `rtnl_unicast()`, `rtnl_notify()`, `rtnl_set_sk_err()`, `rtnetlink_put_metrics()`, `rtnl_put_cacheinfo()`, `rtmsg_ifinfo()`, `rtmsg_ifinfo_newnet()`, `rtmsg_ifinfo_build_skb()`, `rtmsg_ifinfo_send()`, `rtnl_lock()`, `rtnl_unlock()`, `rtnl_trylock()`, `rtnl_lock_interruptible()`, `rtnl_lock_killable()`, `refcount_dec_and_rtnl_lock()`, per-net RTNL lock helpers, `dev_ingress_queue()`, `dev_ingress_queue_rcu()`, `dev_ingress_queue_create()`, `rtnetlink_init()`, `__rtnl_unlock()`, `rtnl_kfree_skbs()`, default FDB/bridge helpers, `rtnl_offload_xstats_notify()`, `rtnl_has_listeners()`, `rtnl_notify_needed()`, and `netif_set_operstate()`. It also defines `struct ndo_fdb_dump_context`.

## Control flow, state, and persistence
Network configuration writers take RTNL or per-net RTNL, update RCU-protected netdev state, and emit rtnetlink multicast/unicast notifications when listeners or echo flags require it. Helper macros combine RCU dereference/update with lockdep checks. Global state includes unregister wait queues/counts and network namespace rwsems declared here but defined elsewhere.

## Dependencies and integration points
It depends on mutexes, netdevice, wait queues, refcounts, netlink/UAPI rtnetlink, RCU, lockdep, ingress/egress queue configs, bridge/FDB operations, and network namespaces. It is used by virtually all netdevice, address, route, neighbor, bridge, and offload xstats configuration code.

## Risks and test signals
Risks include missing RTNL around netdev mutations, deadlocks from nesting RTNL with driver locks, incorrect RCU pointer replacement, notification storms or missing notifications, and small-RTNL/per-net lock mismatches. Test signals include lockdep assertions, rtnetlink selftests, netdev register/unregister races, listener/echo notification tests, FDB add/del/dump coverage, ingress/egress queue creation, and namespace teardown stress.
