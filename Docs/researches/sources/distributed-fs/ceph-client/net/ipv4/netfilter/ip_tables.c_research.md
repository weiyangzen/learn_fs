# sources/distributed-fs/ceph-client/net/ipv4/netfilter/ip_tables.c

## Purpose
`ip_tables.c` is the legacy IPv4 iptables core: it evaluates IPv4 xtables rules, validates and replaces userspace table blobs, manages match/target module references, exposes the legacy sockopt ABI, supports compat tasks, and registers built-in standard/error targets.

## Important APIs, Types, And Functions
Exports are `ipt_alloc_initial_table()`, `ipt_do_table()`, `ipt_register_table()`, and `ipt_unregister_table_exit()`. Major internals are `ip_packet_match()`, `trace_packet()`, `mark_source_chains()`, `find_check_match()`, `find_check_entry()`, `translate_table()`, `copy_entries_to_user()`, `do_replace()`, `do_add_counters()`, compat conversion helpers, and sockopt handlers.

## Control Flow
Packet traversal starts at the hook entry offset, matches source/destination masks, interfaces, protocol, fragment state, and all extension matches, updates per-CPU counters, then executes standard jumps/gotos/returns or extension targets. TRACE logging reconstructs chain/rule context when enabled. Replacement validates entry sizes, offsets, hooks, underflows, rule graph loops, match/target modules, and then swaps the table atomically through xtables core.

## State And Persistence
Per-net protocol state is initialized by `xt_proto_init()`. Installed table state is in `struct xt_table_info`: entries, counters, hook/underflow offsets, jump stack, and module refs. It is all in-memory and namespace-scoped.

## Dependencies And Integration Points
It integrates netfilter IPv4 hooks, xtables match/target registry, sockopts, proc/compat infrastructure, module autoloading, per-CPU seqcount counter snapshots, TRACE logging, and table instance modules such as filter, mangle, nat, raw, and security.

## Risks
This file has high ABI and memory-safety exposure. Risks include replacement blob validation gaps, compat offset mistakes, rule graph loop bugs, module reference leaks, counter races, jump stack corruption with TEE recursion, fragment handling surprises, and trace path assumptions.

## Test Signals
Exercise malformed table replacement, loop/goto/return chains, all standard verdicts, match/target module load failures, counter add/get, 32-bit compat replace/get, TEE recursion, TRACE logging, fragment matching, namespace lifecycle, and table unregister while packets are traversing.
