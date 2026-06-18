# sources/distributed-fs/ceph-client/net/ipv6/ip6_fib.c

Purpose: implements the IPv6 Forwarding Information Database radix tree, per-net FIB table lifecycle, route add/delete/lookup/walk/dump, route garbage collection, notifier integration, and `/proc/net/ipv6_route` iteration.

Important APIs, types, and functions: exported or cross-module functions include `fib6_info_alloc()`, `fib6_info_destroy_rcu()`, `fib6_new_table()`, `fib6_get_table()`, `fib6_lookup()`, `fib6_tables_dump()`, `fib6_metric_set()`, `fib6_add()`, `fib6_node_lookup()`, `fib6_locate()`, `fib6_del()`, `fib6_clean_all()`, `fib6_run_gc()`, `fib6_init()`, and `fib6_gc_cleanup()`. Core types are `fib6_node`, `fib6_info`, `fib6_table`, `fib6_walker`, and `fib6_cleaner`.

Control flow: per-net init creates stats, table hash, main/local tables, walker locks, and GC timer. Adds descend or split the radix tree with `fib6_add_1()`, optionally enter source-specific subtrees, then insert or replace `fib6_info` in metric order with ECMP sibling handling and notifier emission. Deletes unlink a route, rebalance siblings, adjust active walkers, repair empty intermediate nodes, purge cached routes/exceptions, and notify listeners. Lookups descend by destination and optional source prefix then backtrack to the longest valid route node. Dumps and proc iteration use reentrant walkers that can suspend and resume after skb fill or tree serial changes. GC scans per-table gc lists for expiring routes and exceptions and reschedules the per-net timer if more work remains.

State and persistence: all state is per network namespace and memory-resident: FIB table hash, radix nodes from `fib6_node_kmem`, route entries, peer bases, route stats, serial numbers, walker list, and GC timer. RCU protects readers; table locks protect mutations. `fn_sernum` and table `fib_seq` signal route changes to caches, dumps, and notifiers.

Dependencies and integration points: integrates with IPv6 route lookup/output code, rtnetlink `RTM_GETROUTE`, fib notifier chains, nexthop objects, lightweight tunnels, addrconf routes, dst metrics, exception caches, BPF iterators, procfs, and optional multiple-table/source-subtree configs.

Risks: this snapshot shows duplicated or malformed source fragments around `call_fib6_multipath_entry_notifiers()` and a duplicated comment terminator near tree insertion, which are compile-risk signals. Algorithmically, radix tree repair and active walker adjustment are high-risk because deletion can occur during dumps/GC. ECMP sibling counters use `BUG_ON()` for invariant breaks. Per-cpu cached route cleanup must be synchronized with `fib6_destroying` and memory barriers.

Test signals: route add/replace/delete with and without `NLM_F_CREATE`/`NLM_F_REPLACE`, source-specific routes, ECMP append/replace/delete, nexthop object deletion, concurrent route dumps while mutating routes, GC of expiring addrconf routes and exceptions, namespace teardown, proc/BPF route iteration, and lockdep/RCU coverage.
