# sources/distributed-fs/ceph-client/net/ipv6/netfilter/ip6_tables.c

Purpose: Implements legacy IPv6 ip6tables rule evaluation, table registration/replacement, userspace sockopt ABI, counters, compatibility conversion, and built-in standard/error targets.

Important APIs/types/functions: Exports `ip6t_alloc_initial_table`, `ip6t_register_table`, `ip6t_unregister_table_exit`, and `ip6t_do_table`. Core functions include `ip6_packet_match`, `mark_source_chains`, `translate_table`, `find_check_entry`, `cleanup_entry`, `get_info`, `get_entries`, `do_replace`, `do_add_counters`, compat translation helpers, and sockopt handlers `do_ip6t_set_ctl`/`do_ip6t_get_ctl`.

Control flow: Packet evaluation starts at the hook entry, matches IPv6 source/destination/interface/protocol and extension-header location, runs xt matches, updates per-CPU counters, and executes standard or extension targets. Standard positive verdicts jump/goto inside the table with a per-CPU jump stack; negative verdicts accept/drop/return. Userspace replacement copies a table blob, validates entry sizes/hook underflows, computes source-chain reachability and loop safety, resolves match/target modules, then atomically swaps table info and returns old counters. Get paths snapshot counters and translate kernel entries back to userspace. Compat paths adjust entry, match, target, hook, and verdict offsets for 32-bit userspace.

State and persistence: Runtime state includes per-net xtables protocol state, registered tables, `xt_table_info` blobs, per-CPU counters, jump stacks, module references, and sockopt registration. Rules persist only in kernel memory until replaced, table unregistered, module unloaded, or namespace destroyed.

Dependencies/integration: Depends on x_tables core, nf_sockopt, module autoloading, netfilter hook ops, optional trace logging, compat infrastructure, and table modules such as `ip6table_filter`.

Risks and test signals: Highest risks are userspace blob validation, loop detection, offset arithmetic, compat conversion, counter consistency under concurrent packet traversal, module reference leaks, and jumpstack recursion with TEE. Tests should cover malformed replace blobs, invalid hooks/underflows, loops, missing modules, concurrent replace/get/add counters under traffic, 32-bit compat ip6tables, TRACE logging, goto versus jump semantics, and namespace teardown.
