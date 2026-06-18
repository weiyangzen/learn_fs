# sources/distributed-fs/ceph-client/net/ipv4/fib_trie.c

## Purpose
`fib_trie.c` implements the IPv4 FIB table backing store using a level-compressed trie. It is the route insertion, deletion, lookup, flush, notification, dump, and procfs inspection engine behind IPv4 routing tables. The implementation optimizes longest-prefix match with compressed path traversal and adaptive tnode resizing.

## Important APIs, Types, And Functions
Core data structures are `struct key_vector`, `struct tnode`, `struct trie`, `struct fib_alias`, and `struct fib_table`. Leaves hold hlist chains of aliases sorted by suffix length, table id, DSCP, and priority; internal tnodes hold child vectors plus parent, empty-child, and full-child accounting.

External entry points include `fib_table_insert`, `fib_table_delete`, `fib_table_lookup`, `fib_table_dump`, `fib_table_flush`, `fib_table_flush_external`, `fib_trie_unmerge`, `fib_trie_table`, `fib_free_table`, `fib_notify`, `fib_info_notify_update`, `fib_alias_hw_flags_set`, `fib_proc_init`, and `fib_proc_exit`. `fib_table_lookup` and `fib_lookup_good_nhc` are exported for route resolution. Initialization creates `ip_fib_alias` and `ip_fib_trie` slab caches in `fib_trie_init`.

Internal maintenance revolves around `fib_find_node`, `fib_find_alias`, `fib_insert_node`, `fib_insert_alias`, `fib_remove_alias`, `leaf_walk_rcu`, `resize`, `inflate`, `halve`, `collapse`, `node_push_suffix`, and `node_pull_suffix`.

## Control Flow
Insert starts by building a `fib_info`, locating the leaf for `cfg->fc_dst`, then finding the insertion point for the prefix suffix length, DSCP, table id, and priority. Existing exact entries honor `NLM_F_EXCL`, `NLM_F_REPLACE`, and `NLM_F_APPEND`. Replacements allocate a new alias, swap it with `hlist_replace_rcu`, notify listeners if it is the effective route, emit `RTM_NEWROUTE`, and release the old `fib_info`. Creates allocate a `fib_alias`, insert it into an existing leaf or create a new leaf/tnode path, update default-route count, flush route cache, and emit netlink notifications.

Lookup descends by key from the trie root, checks compressed-prefix mismatches, then backtracks through candidate prefixes until a semantic match succeeds. Alias filtering checks prefix coverage, DSCP mask, dead `fib_info`, scope, route type error, nexthop object state, link-down policy, requested output interface, and nexthop selection. On success it fills `struct fib_result`; on miss it backtracks until no candidate remains and returns `-EAGAIN`.

Delete finds the leaf and alias matching route config, sends delete or replace notifier semantics based on the next visible alias, emits `RTM_DELROUTE`, removes the alias, possibly removes the leaf, rebalances the trie, releases `fib_info`, and frees alias memory through RCU.

Flush walks the trie in reverse order, removing dead or error aliases, updating suffixes, resizing tnodes, and emitting notifications when needed. Dump and notification paths use `leaf_walk_rcu` to produce netlink rows or notifier events without changing trie structure. Procfs iterators render `/proc/net/fib_trie`, `/proc/net/fib_triestat`, and `/proc/net/route`.

## State And Persistence
State is in memory per network namespace as `fib_table` objects in `net->ipv4.fib_table_hash`. Tables may share trie data for local/main aliasing until `fib_trie_unmerge` clones local entries. Memory is RCU protected for readers and RTNL protected for writers. Freed tnodes and aliases are deferred through `call_rcu`; bulk dirty trie memory is throttled by `sysctl_fib_sync_mem`. Optional per-CPU trie stats persist for table lifetime when `CONFIG_IP_FIB_TRIE_STATS` is enabled.

## Dependencies And Integration Points
This file integrates with route netlink (`rtmsg_fib`, `fib_dump_info`), FIB notifier chains (`call_fib4_notifier(s)`), nexthop and `fib_info` management, route cache flushing, IPv4 sysctls, procfs seq files, tracepoints, RCU, RTNL, slab/vmalloc allocation, and network namespace table hashes. Consumers depend on the lookup contract and on dump/notify ordering for route monitoring.

## Risks
The riskiest areas are RCU/list lifetime, tnode resize correctness, alias ordering, and semantic lookup backtracking. A wrong suffix update can lose longest-prefix matches. Replacement notification rollback must preserve alias ordering and references. Shared trie aliasing between local and main tables makes flush/unmerge behavior subtle. Procfs and dump iterators must not dereference freed nodes while walking under RCU.

## Test Signals
Useful signals include route add/replace/delete coverage through rtnetlink, DSCP route lookup tests, multipath and nexthop link-state lookup tests, local/main table unmerge tests, route flush tests with dead nexthops and error routes, notifier behavior for first-visible alias changes, `/proc/net/route` compatibility checks, `/proc/net/fib_trie` traversal under concurrent updates, and stress tests with route churn under RCU debugging and KASAN.
