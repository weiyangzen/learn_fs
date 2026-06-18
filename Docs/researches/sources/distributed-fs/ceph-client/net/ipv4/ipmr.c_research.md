# sources/distributed-fs/ceph-client/net/ipv4/ipmr.c

## Purpose
`ipmr.c` implements IPv4 multicast routing (`RTNL_FAMILY_IPMR`): multicast routing table creation, VIF lifecycle, multicast forwarding cache (MFC) insertion/deletion, unresolved cache upcalls to a routing daemon, PIM register handling, rtnetlink/proc observability, and packet forwarding from `ip_mr_input()` and `ip_mr_output()`.

## Important APIs, Types, And Functions
Core exported entry points are `ip_mr_init()`, `ip_mroute_setsockopt()`, `ip_mroute_getsockopt()`, `ipmr_ioctl()`, `ip_mr_input()`, `ip_mr_output()`, `ipmr_get_route()`, and compat ioctl helpers. The central state is `struct mr_table`, `struct vif_device`, and IPv4-specific `struct mfc_cache`, backed by an rhashtable keyed by `(origin, multicast group)`. Multiple-table builds add `fib_rules_ops` via `ipmr_rule_*()`, while single-table builds store `net->ipv4.mrt`. VIF management is in `vif_add()` and `vif_delete()`. MFC management is in `ipmr_mfc_add()`, `ipmr_mfc_delete()`, `ipmr_cache_unresolved()`, `ipmr_cache_resolve()`, and `mroute_clean_tables()`.

## Control Flow
Initialization allocates the `mfc_cache` slab, registers per-net state, netdevice notifier, optional PIM protocol handler, and rtnetlink handlers. Userspace opens a raw IGMP socket and drives `MRT_INIT`, VIF, MFC, PIM, assert, flush, and table options through `ip_mroute_setsockopt()`. Packet input looks up the multicast table with route rules, finds exact or wildcard MFC entries, queues unresolved packets for daemon upcall when needed, and otherwise fans packets out through VIFs with TTL thresholds and netfilter forward hooks. Local multicast output uses the same cache model when `IPSKB_MCROUTE` is set, otherwise falls back to normal multicast output.

## State And Persistence
State is per network namespace and in-memory only: `mr_table` lists/rhashtables, VIF array, unresolved queue, route socket pointer, PIM flags, counters, timers, notifier seq, and optional fib rules. Resolved entries are RCU/list/rhashtable managed; unresolved entries are protected by `mfc_unres_lock` and expire after roughly 10 seconds. Device references use RCU plus netdevice trackers; dynamically created tunnel/register netdevices are queued for unregister on cleanup.

## Dependencies And Integration Points
The file integrates raw socket router-alert delivery, rtnetlink route/link operations, fib rules, netdevice unregister notifiers, procfs files `ip_mr_vif` and `ip_mr_cache`, PIM v1/v2 protocol handlers, tunnel devices, netconf notifications, netfilter forward hooks, switchdev offload marks, and shared multicast helpers from `ipmr_base.c`.

## Risks
Major risks are concurrency and lifetime mistakes across RCU, RTNL, `mrt_lock`, `mfc_mutex`, and `mfc_unres_lock`; incorrect unresolved queue accounting; stale device pointers; malformed netlink validation; under/over-forwarding wildcard `(*,G)` or `(*,*)` entries; and subtle routing loops around wrong-IIF asserts, register VIFs, tunnel encapsulation, and local-output multicast routing.

## Test Signals
Useful tests include `MRT_*` socket option permission and length checks, VIF add/delete on normal, tunnel, and register VIFs, MFC add/delete/replace/proxy behavior, unresolved queue timeout and netlink error delivery, PIM register receive paths, `ip route get`/dump for `RTNL_FAMILY_IPMR`, procfs output, namespace teardown, device unregister cleanup, multicast forwarding counters, wrong-IIF assert generation, and netfilter hook interaction during forwarding.
