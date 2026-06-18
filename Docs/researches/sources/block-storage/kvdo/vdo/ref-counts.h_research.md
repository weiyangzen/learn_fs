# File Research: sources/block-storage/kvdo/vdo/ref-counts.h

Declares the reference-count subsystem used by each `vdo_slab`.

Important types:
- `enum reference_status`: logical states for a counter: free, single, shared, provisional.
- `struct reference_block`: tracks one persisted refcount block, including dirty/writing state, allocated counter count, slab journal locks, and per-sector commit points.
- `struct search_cursor`: stores the current block/index/end range for free-block scans.
- `struct ref_counts`: owns the slab pointer, counter array, free count, dirty queue, active I/O count, slab summary update waiter, read-only notifier, shared statistics, persisted origin, latest slab journal point, and flexible array of `reference_block`s.

Public API:
- Construction/destruction: `vdo_make_ref_counts()`, `vdo_free_ref_counts()`.
- State/queries: `vdo_are_ref_counts_active()`, `vdo_get_unreferenced_block_count()`, `vdo_get_available_references()`, `vdo_count_unreferenced_blocks()`.
- Allocation/reference updates: `vdo_allocate_unreferenced_block()`, `vdo_provisionally_reference_block()`, `vdo_adjust_reference_count()`, `vdo_adjust_reference_count_for_rebuild()`, `vdo_replay_reference_count_change()`.
- Persistence/drain: `vdo_save_several_reference_blocks()`, `vdo_save_dirty_reference_blocks()`, `vdo_dirty_all_reference_blocks()`, `vdo_drain_ref_counts()`, `vdo_acquire_dirty_block_locks()`.
- Diagnostics: `vdo_dump_ref_counts()`.

The header exposes enough internals for adjacent slab/journal code to reason about refcount block activity, but most mutation logic stays in `ref-counts.c`.
