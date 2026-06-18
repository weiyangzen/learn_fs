# sources/distributed-fs/ceph-client/include/net/ip6_fib.h

Purpose: Defines the IPv6 forwarding information base data model and exported lookup/update interfaces. It is the core contract between IPv6 route management, policy rules, neighbour/device state, notifier users, BPF route iterators, and route cache/dst users.

Important APIs/types/functions: `fib6_config` carries netlink route mutations, including table, metrics, source/destination prefixes, gateways, nexthop id, encapsulation, and FDB flags. `fib6_node`, `fib6_table`, `fib6_info`, `fib6_nh`, `rt6_info`, and `fib6_result` model the trie, tables, routes, nexthops, dst entries, and lookup result. Key APIs include `fib6_get_table`, `fib6_new_table`, `fib6_rule_lookup`, `fib6_lookup`, `fib6_table_lookup`, `fib6_select_path`, `fib6_node_lookup`, `fib6_locate`, `fib6_add`, `fib6_del`, notifier calls, GC functions, and rules helpers.

Control flow: Readers use RCU-protected trie/table traversal, perform table or rule lookup, then call selection helpers for multipath/nexthop choice. Writers add/delete `fib6_info` entries under table locks and update serial numbers/notifiers. Inline expiry helpers toggle `RTF_EXPIRES`; cookie helpers pair memory barriers with serial-number updates.

State and persistence: Route state is in per-net `fib6_table` hashes, trie nodes, route refcounts, per-route metrics, GC hlist links, sibling lists, exception buckets, and per-cpu dst caches. It is in-memory kernel state, reconstructed from configuration/control plane rather than persisted by this header.

Dependencies/integration: Depends on IPv6 route UAPI, `dst`, `flowi6`, IPv4 shared `fib_nh_common`, inet peers, nexthop objects, fib notifiers, netlink, RCU, BPF iterators, and optional IPv6 multiple-table/subtree/rules support.

Risks: Incorrect lock/RCU pairing can expose freed routes; missed refcounting around `fib6_info_hold_safe` can use stale entries; wrong GC list handling can leak routes or age exceptions incorrectly; source-subtree counters can desynchronize if increments/decrements are not paired. Test signals include IPv6 route add/delete/dump, policy rules, multipath, route expiry, PMTU exception GC, notifier consumers, BPF route iteration, and IPv6 disabled build stubs.
