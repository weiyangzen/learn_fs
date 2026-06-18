<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mroute_base.h -->
# sources/distributed-fs/ceph-client/include/linux/mroute_base.h

## Purpose
`mroute_base.h` provides common multicast routing table, virtual interface, multicast forwarding cache, notifier, lookup, dump, and proc-iteration infrastructure shared by IPv4 and IPv6 multicast routing.

## Important APIs, Types, and Functions
Core types include `struct vif_device`, `struct vif_entry_notifier_info`, `struct mr_mfc`, `struct mfc_entry_notifier_info`, `struct mr_table_ops`, `struct mr_table`, `struct mr_vif_iter`, and `struct mr_mfc_iter`. Helpers include `mr_call_vif_notifier()`, `mr_call_vif_notifiers()`, `VIF_EXISTS`, `mr_cache_put()`, `mr_cache_hold()`, `mr_call_mfc_notifier()`, `mr_call_mfc_notifiers()`, `mr_can_free_table()`, `vif_device_init()`, `mr_table_free()`, `mr_table_alloc()`, `mr_mfc_find_parent()`, `mr_mfc_find_any_parent()`, `mr_mfc_find_any()`, `mr_mfc_find()`, `mr_fill_mroute()`, `mr_table_dump()`, `mr_rtm_dumproute()`, `mr_dump()`, and proc sequence helpers.

## Control Flow and State
Protocol-specific code allocates `struct mr_table` with hash parameters and an expire timer. VIF operations initialize table entries and emit FIB notifications. MFC entries are unresolved with queued skbs until userspace resolves them, or resolved with TTL arrays, counters, last-use/assert timestamps, and refcounts. Route dumps walk hash/list state under appropriate locks and RCU. Proc iteration switches between unresolved and resolved cache lists, unlocking in `mr_mfc_seq_stop()`.

## State and Persistence Behavior
State is per-network-namespace runtime routing state. VIFs hold RCU-protected device pointers and ref trackers. MFC entries are refcounted and freed via RCU callback. Unresolved entries use timers and queues; resolved entries hold atomic byte/packet/wrong-if counters.

## Dependencies and Integration Points
It depends on netdevice, rhashtable, spinlocks, net namespaces, sockets, fib notifiers, IP FIB, timers, RCU work, seq_file, and netlink dump paths. IPv4 and IPv6 wrappers provide protocol-specific keys and route filling.

## Risks
RCU and refcount correctness are critical. Notifier callers require correct RTNL assertions and sequence increments. Unresolved queue length must be bounded. Proc iteration must unlock the right list. Common structs are embedded first in protocol-specific cache structs for casting.

## Test Signals
IPv4/IPv6 multicast route add/delete, unresolved queue expiry, hardware offload notification, netns teardown, route dumps, proc VIF/MFC reads, refcount/RCU debug, and `CONFIG_IP_MROUTE_COMMON=n` stub builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mroute_base.h -->
