
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_set_pipapo.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nft_set_pipapo.c

## Purpose

`nft_set_pipapo.c` implements the PIPAPO nftables set backend for concatenated interval/range keys. It converts ranges to netmask-like rule expansions, classifies packet fields through lookup-table bucket intersections, maps matching rules across fields, and supports maps, objects, timeouts, transactions, GC, and optional AVX2 acceleration.

## Important APIs, Types, and Functions

The exported types are `nft_set_pipapo_type` and, on x86-64, `nft_set_pipapo_avx2_type`. Lookup flows through `nft_pipapo_lookup()`, `pipapo_get_slow()`, and control-plane `nft_pipapo_get()`. Insertion uses `nft_pipapo_insert()`, `pipapo_expand()`, `pipapo_insert()`, and `pipapo_map()`. Transaction state is managed by `pipapo_maybe_clone()`, `pipapo_clone()`, `nft_pipapo_commit()`, and `nft_pipapo_abort()`. Removal and GC use `pipapo_drop()`, `nft_pipapo_remove()`, `pipapo_gc_scan()`, and `pipapo_gc_queue()`.

## Control Flow

Initialization creates an empty active match object with one field per concatenated component and per-CPU scratch pointers. Insertions operate on a mutable clone, reject exact duplicates and partial overlaps, validate per-field start/end ordering, expand each field range into one or more rules, resize lookup/mapping tables, ensure scratch capacity, and map final rules to the inserted element. Datapath lookup reads only the active RCU match copy and uses generation mask zero because pending elements live only in the clone. Commit optionally scans expired entries in the clone, atomically swaps clone into `match`, frees the old copy after RCU, and queues collected elements.

## State and Persistence Behavior

Persistent set state is split between active `match` and pending `clone`. Each field owns lookup tables, mapping tables, rule counts, allocation size, group width, and per-CPU scratch maps. Table group width dynamically switches between four-bit and eight-bit buckets based on size thresholds. Timeouts are collected opportunistically on commit rather than by periodic work.

## Dependencies and Integration Points

The backend depends on nf_tables set APIs, generation masks, set element extensions, transaction GC helpers, per-CPU local locks, bitmap helpers, RCU, and the optional AVX2 header. It is selected for interval sets with at least two concatenated fields.

## Risks and Test Signals

Risks include range expansion overflow, mapping-table compaction errors, clone/commit generation mismatches, scratch reallocation on possible CPUs, overlap detection, endian-sensitive range expansion, and timeout GC only running when commits occur. Test concatenated IPv4/port and IPv6 ranges, exact duplicate versus partial overlap, add/delete/abort/commit, timeout expiry, maps/objects, AVX2 and non-AVX2 kernels, and memory pressure paths in resize/clone.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_set_pipapo.c -->
