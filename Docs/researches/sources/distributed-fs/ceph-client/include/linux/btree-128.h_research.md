## sources/distributed-fs/ceph-client/include/linux/btree-128.h

**Purpose:** This header provides typed wrappers for the generic kernel B+Tree using 128-bit keys represented as two `u64` words.

**Important APIs/types/functions:** It declares `extern struct btree_geo btree_geo128` and `struct btree_head128`. Inline wrappers include `btree_init_mempool128`, `btree_init128`, `btree_destroy128`, `btree_lookup128`, `btree_get_prev128`, `btree_insert128`, `btree_update128`, `btree_remove128`, `btree_last128`, `btree_merge128`, `btree_visitor128`, `btree_grim_visitor128`, and `btree_for_each_safe128`. `visitor128_t` gives callbacks two `u64` key parts.

**Control flow, state, persistence:** The wrappers convert `(k1, k2)` into a two-element `u64 key[2]` and pass it to generic B+Tree functions with `btree_geo128`. Tree state is stored in the embedded `struct btree_head h`; memory allocation and node lifetime are handled by the generic implementation/mempool.

**Dependencies/integration:** Must be included after `btree.h` has declared the generic types/functions. It integrates with users that need compound keys and typed visitors without manually building `unsigned long *` keys.

**Risks and test signals:** Risks are key-word ordering mismatches, stack key lifetime assumptions outside synchronous calls, partial merge failures, and 32-bit architecture casting assumptions. Test signals include insert/lookup/remove/update of two-word keys, reverse iteration through `btree_for_each_safe128`, visitor traversal, and merge failure injection.
