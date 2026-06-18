# sources/distributed-fs/ceph-client/include/net/nexthop.h

Purpose: defines the generic nexthop object model shared by IPv4 FIB, IPv6 FIB, FDB routes, resilient nexthop groups, and switchdev/offload notification consumers.

Important APIs and types: `struct nexthop`, `struct nh_info`, `struct nh_group`, `struct nh_grp_entry`, `struct nh_res_table`, and `struct nh_res_bucket` model single and grouped nexthops. `struct nh_config` is the netlink/control-plane parse product. Notifier payloads describe single nexthops, groups, resilient tables/buckets, and group hardware statistics. Helpers include `nexthop_find_by_id()`, `nexthop_get()/put()`, `nexthop_select_path()`, `nexthop_fib_nhc()`, IPv6/FDB result helpers, and offload flag/stat update APIs.

Control flow: route lookups hold RCU or RTNL, select a single nexthop from a group, then expose the embedded `fib_nh_common`, `fib_nh`, or `fib6_nh`. Netlink changes replace RCU pointers and notify listeners; resilient groups maintain bucket tables and migration/upkeep state.

State and persistence: all state is netns-local kernel memory: rb-tree membership, FIB user lists, FDB users, group backrefs, refcounts, resilient bucket timestamps, hardware packet counters, and offload/trap state. Persistence is delegated to userspace route configuration.

Dependencies and integration points: depends on netdevice, netlink, IPv4/IPv6 FIB internals, RCU/refcounting, notifier blocks, switchdev-style offloads, and rtnetlink nexthop configuration.

Risks and test signals: risks include stale RCU dereferences, unbalanced refcounts, resilient bucket migration mistakes, mixed IPv4/IPv6 group handling, and notifier/offload drift. Test nexthop create/replace/delete, multipath selection, blackhole/FDB nexthops, device removal, IPv6 route interaction, resilient bucket replacement, and hardware stats reporting.
