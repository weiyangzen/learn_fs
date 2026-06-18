<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_recent.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_recent.c

## Purpose
`xt_recent.c` implements the stateful `recent` match, maintaining per-net named lists of recently seen IPv4/IPv6 addresses with timestamp rings and optional TTL checks. It also exposes `/proc/net/xt_recent/*` for inspection and manual add/remove/flush operations.

## Important APIs, Types, and Functions
State is held in `struct recent_net`, `struct recent_table`, and `struct recent_entry`. Key helpers are `recent_entry_lookup()`, `recent_entry_init()`, `recent_entry_update()`, `recent_entry_remove()`, `recent_entry_reap()`, `recent_table_lookup()`, and `recent_table_flush()`. `recent_mt()` performs packet matching. `recent_mt_check_v0()` and `recent_mt_check_v1()` validate rules and create/reuse tables; `recent_mt_destroy()` releases references. Procfs support uses `recent_seq_*()` and `recent_mt_proc_write()`.

## Control Flow, State, and Persistence
Rule insertion validates exactly one of SET, REMOVE, CHECK, or UPDATE, validates modifiers such as TTL and REAP, sizes the timestamp ring from hit count, and creates a named table if needed. Packet evaluation masks source or destination address, optionally uses TTL/hop-limit, looks up the entry, and performs SET, REMOVE, CHECK, or UPDATE semantics. Tables maintain hash buckets plus an LRU list capped by `ip_list_tot`; timestamp rings persist until entry removal, table flush, namespace teardown, or module unload.

## Dependencies and Integration Points
The module uses per-net generic storage, procfs, seq_file, spinlock/mutex coordination, random jhash seeds, IPv4/IPv6 address helpers, and x_tables match lifecycle. Module parameters control table size, hash size, proc permissions, owner uid/gid, and backward-compatible packet-list sizing.

## Risks and Test Signals
High-risk areas are global lock contention, proc write parsing, table resize flush on larger hit counts, timestamp ring wrap, TTL adjustment for forwarded output packets, namespace proc cleanup before rule destruction, and memory sizing up to `XT_RECENT_MAX_NSTAMPS`. Tests should cover all operations, seconds/hitcount/reap combinations, TTL matching, masks, IPv4/IPv6 parsing in proc writes, add/remove/flush proc commands, LRU eviction, table sharing/refcounts, namespace teardown, invalid flags, and module parameter bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_recent.c -->
