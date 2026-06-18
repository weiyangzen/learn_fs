# sources/distributed-fs/ceph-client/include/net/ip_fib.h

Purpose: Defines the IPv4 FIB data structures, route lookup contracts, nexthop/common nexthop state, route-table operations, policy-rule hooks, multipath hashing, source validation, notifier events, and proc/dump helpers.

Important APIs/types/functions: `fib_config` is the netlink route-change description. `fib_nh_common` is shared by IPv4 and IPv6 nexthops and holds device, gateway, lwtunnel state, weight, per-cpu output routes, input route, and PMTU exceptions. `fib_nh`, `fib_info`, `fib_result`, `fib_table`, and notifier structures cover route sharing, trie lookup results, and hardware/offload events. APIs include `fib_table_lookup/insert/delete/dump/flush`, `fib_lookup`, rules helpers, `fib_validate_source`, device sync, MTU sync, multipath hash/path selection, nexthop init/release, trie table creation, and nexthop netlink encoding.

Control flow: `fib_lookup` chooses direct main/default table lookup or policy-rule lookup depending on `CONFIG_IP_MULTIPLE_TABLES` and per-net custom-rule state. Route results carry selected nexthop common state and are later refined by multipath selection. Early flow dissection populates ports/protocol only when rules require L4 keys.

State and persistence: In-memory per-net IPv4 route tables, route info refcounts, nexthop exception hash buckets, per-cpu route caches, metrics, route-class IDs, and notifier state are maintained by implementation files. This header exposes refcount transitions through `fib_info_hold/put`.

Dependencies/integration: Integrates with `flowi4`, fib rules/notifiers, inet DSCP, inetpeer, lwtunnel, L3 master devices, netlink route policies, nexthop objects, and procfs.

Risks: FIB lookup must run under the right RCU/rtnl context; no-ref lookups require callers not to retain routes unsafely; DSCP masked match affects route selection compatibility; multipath hash fields are UAPI and must remain append-only. Test signals include single/multiple table builds, route add/delete/dump, reverse-path/source validation, device down/up/MTU events, route exceptions, classid, and multipath hashing with configurable fields.
