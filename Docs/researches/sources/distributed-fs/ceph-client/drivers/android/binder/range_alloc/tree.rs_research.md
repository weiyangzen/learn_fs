# sources/distributed-fs/ceph-client/drivers/android/binder/range_alloc/tree.rs

Purpose: implements the scalable RBTree-backed Binder mmap range allocator used after the small array fills. It stores both allocated descriptors and free descriptors, plus a second tree keyed by free-range size for best-fit allocation.

Important APIs/types/functions: `TreeRangeAllocator<T>` owns `tree: RBTree<offset, Descriptor<T>>`, `free_tree: RBTree<(size, offset), ()>`, total size, and `free_oneway_space`. `Descriptor<T>` carries offset, size, and optional `DescriptorState` plus a reserved free-tree node. `ReserveNewTreeAlloc` and `FromArrayAllocs` preallocate RBTree nodes. Main methods are `from_array`, `reserve_new`, `reservation_abort`, `reservation_commit`, `reserve_existing`, `take_for_each`, `is_empty`, and `low_oneway_space`.

Control flow: `from_array` drains sorted array descriptors, emits free descriptors for gaps, inserts allocated descriptors, and records every free range by `(size, offset)`. `reserve_new` finds the smallest free range at least as large as requested, removes it from `free_tree`, turns the front of that descriptor into a reserved allocation, and inserts a remainder descriptor when needed. `reservation_abort` validates that the descriptor is reserved, changes it to free, merges adjacent free descriptors, updates `free_tree`, and computes newly free page indices. Commit and reserve-existing change descriptor state without moving ranges.

State and persistence: tree state mirrors process mmap buffer reservations and allocations. Free descriptors are persistent allocator state and are merged to avoid adjacent free ranges. Oneway free space is maintained independently from geometric free space.

Dependencies and integration points: selected by `range_alloc/mod.rs` when descriptor count grows. It depends on kernel `RBTree`, preallocated node reservations, page constants, `DescriptorState`, `FreedRange`, `Range`, and seq-file debugging.

Risks: dual-tree consistency is critical; every free range in `tree` must have exactly one matching key in `free_tree`. Merging during abort must remove stale free keys before mutating sizes. Descriptor state uses `try_change_state` to restore state on errors; bypassing it could lose allocations. Best-fit relies on tuple ordering, so changing `FreeKey` semantics affects fragmentation.

Test signals: allocate exact-fit and split-fit ranges, free with previous/next/both-side merging, unaligned page-boundary freed-range expansion, `free_tree` lookup after many operations, oneway quota and spam checks, array migration preserving descriptors, and collapse to empty after all buffers are aborted.
