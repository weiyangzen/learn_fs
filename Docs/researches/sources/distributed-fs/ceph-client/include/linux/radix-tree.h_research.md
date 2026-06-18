# sources/distributed-fs/ceph-client/include/linux/radix-tree.h

Purpose: provides the legacy radix-tree API as an XArray-backed compatibility interface, including lookup, insert/delete, replacement, tag operations, gang lookup, preload, IDR free-slot search, and iteration macros.

Important APIs and types: `radix_tree_root` aliases `xarray`, and `radix_tree_node` aliases `xa_node`. `struct radix_tree_preload` manages per-CPU preallocated nodes protected by `local_lock_t`. Slot encoding uses low bits to distinguish data pointers, internal nodes, and value entries. `struct radix_tree_iter` tracks chunk index, next index, tag mask, and node. Key APIs include `radix_tree_insert()`, lookup/slot lookup, replace/delete, gang lookup, preload, tag set/clear/get/tagged, `radix_tree_next_chunk()`, `radix_tree_next_slot()`, and `radix_tree_for_each_slot()`/`radix_tree_for_each_tagged()`.

Control flow: users optionally preload nodes, perform locked updates to insert/delete/tag/replace entries, and may perform selected lockless lookups under RCU. Iteration proceeds by chunks found from `next_index`; tagged iteration consumes a per-chunk tag bitmask, and retry/resume helpers handle concurrent modification or lock dropping.

State and persistence: state is in-memory XArray/radix-tree nodes, root flags/tags, per-node slots/tags, and per-CPU preload lists. No persistence exists.

Dependencies and integration points: depends on bitops, GFP, list, lockdep, percpu, preempt, RCU, spinlocks, XArray, and local locks. It integrates older radix-tree users with the modern XArray implementation.

Risks and test signals: risks include storing misaligned/value/internal-looking pointers, freeing objects before RCU readers finish, relying on tag reads under concurrent updates, iterator misuse after deletion, preload local-lock imbalance, and legacy API assumptions diverging from XArray behavior. Test lockless lookup under RCU, concurrent insert/delete/tag operations, gang lookup/tagged lookup, iterator retry/resume, IDR allocation paths, and memory pressure with preload.
