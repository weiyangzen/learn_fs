<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_hashlimit.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_hashlimit.c

## Purpose
`xt_hashlimit.c` implements the stateful `hashlimit` match: a per-key token-bucket or rate-window limiter where keys can include source/destination address and source/destination port. It supports IPv4 and optional IPv6, packet and byte modes, multiple UAPI revisions, and `/proc/net/{ipt_hashlimit,ip6t_hashlimit}` visibility.

## Important APIs, Types, and Functions
Key state types are `struct hashlimit_net`, `struct dsthash_dst`, `struct dsthash_ent`, and `struct xt_hashlimit_htable`. Table lifecycle is handled by `htable_create()`, `htable_find_get()`, `htable_put()`, `htable_gc()`, and `htable_selective_cleanup()`. Entry lifecycle uses `dsthash_find()`, `dsthash_alloc_init()`, and `dsthash_free()`. Rate accounting is in `rateinfo_init()`, `rateinfo_recalc()`, `user2credits()`, `user2credits_byte()`, `user2rate()`, and `hashlimit_byte_cost()`. Packet matching is in `hashlimit_init_dst()` and `hashlimit_mt_common()`, wrapped by revision-specific match/check/destroy functions.

## Control Flow, State, and Persistence
Rule insertion validates masks, mode bits, intervals, overflow limits, and proc names, then reuses or creates a named table in the current net namespace. Table size defaults from RAM, is capped by `HASHLIMIT_MAX_SIZE`, and owns an RCU hash array plus deferrable garbage-collection work. Packet evaluation builds a masked key from requested IPv4/IPv6 addresses and ports, rejects non-first fragments when port hashing is needed, looks up or allocates a locked entry, refreshes expiry, recalculates credit/window state, then returns under-limit or over-limit according to `XT_HASHLIMIT_INVERT`.

## Dependencies and Integration Points
The module integrates with x_tables, per-net generic storage, procfs seq files, RCU hlist traversal, jhash, random hash seeds, slab allocation, delayed work, and IPv4/IPv6 extension-header helpers. `/proc` seq output reports expiry and rate state for each bucket using revision-appropriate display logic.

## Risks and Test Signals
High-risk areas are concurrent entry creation, RCU deletion, delayed-work teardown, overflow-prone credit conversion, byte-mode refill semantics, rate-match window math, IPv6 prefix masking, port hashing with fragments, and named table sharing across rules. Tests should cover revisions 1/2/3, packet and byte modes, rate-match interval behavior, burst handling, table reuse/refcounting, max/size clamps, proc creation/removal and seq reads, IPv4/IPv6 masks, fragmented packets causing hotdrop when ports are required, GC expiry, namespace teardown, and allocation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_hashlimit.c -->
