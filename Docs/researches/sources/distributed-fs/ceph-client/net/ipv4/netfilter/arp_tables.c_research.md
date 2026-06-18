# sources/distributed-fs/ceph-client/net/ipv4/netfilter/arp_tables.c

## Purpose
`arp_tables.c` is the legacy arptables core: it evaluates ARP xtables rules, validates and installs userspace-provided ARP table replacements, exposes sockopt ABIs, handles counters and compat conversion, and registers built-in standard/error targets.

## Important APIs, Types, And Functions
Exports are `arpt_alloc_initial_table()`, `arpt_do_table()`, `arpt_register_table()`, and `arpt_unregister_table()`. Important internals include `arp_packet_match()`, `translate_table()`, `mark_source_chains()`, `find_check_entry()`, `copy_entries_to_user()`, `do_replace()`, `do_add_counters()`, compat translate/copy helpers, `do_arpt_set_ctl()`, and `do_arpt_get_ctl()`.

## Control Flow
Packet evaluation pulls the full ARP header, matches opcode/hardware/protocol lengths, source/target hardware and IP addresses, and in/out interface masks, then executes standard jumps/returns or extension targets. Table replacement copies a user blob, validates entry sizes, hook/underflow offsets, rule graph loops, target modules, and counters, then atomically swaps it into the xt table. Sockopts gate all operations on `CAP_NET_ADMIN`.

## State And Persistence
Per-net xtables state is initialized by `xt_proto_init()`. Table state lives in `struct xt_table_info` with per-CPU counters, hook offsets, underflows, stack size, and installed target module references. State is in-memory and namespace-scoped.

## Dependencies And Integration Points
It integrates xtables core APIs, ARP netfilter family hooks, `nf_sockopt_ops`, module autoloading, vmalloc counters, compat syscall translation, and table instance modules such as `arptable_filter.c`.

## Risks
This is a high-risk userspace ABI parser. Risks include integer/offset validation bugs, loop detection errors, compat size conversion mistakes, counter snapshot races, module reference leaks, FireWire ARP target-address differences, and jump-stack overflow.

## Test Signals
Test malformed replacement blobs, hook and underflow validation, jump loops, unknown targets, compat 32-bit replace/get paths, counter add/get, standard verdicts, error target behavior, FireWire ARP matching, namespace init/exit, and table unregister cleanup.
