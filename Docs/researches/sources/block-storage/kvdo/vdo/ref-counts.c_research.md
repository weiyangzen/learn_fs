# File Research: sources/block-storage/kvdo/vdo/ref-counts.c

Implements the per-slab physical block reference-count engine and its persistence path. It owns in-memory byte counters, free-block searching, provisional allocations, replay/rebuild adjustments, dirty reference-count block writeback, loading saved reference blocks, and coordination with slab journal locks and slab summary cleanliness.

Key behavior:
- `vdo_make_ref_counts()` allocates a `struct ref_counts` with an extended `reference_block` array and a padded counter array sized by `vdo_get_saved_reference_count_size()`.
- Reference counts are interpreted as `RS_FREE`, `RS_SINGLE`, `RS_SHARED`, or `RS_PROVISIONAL`.
- Data increments transition free/provisional blocks to count `1`, increment shared counts up to `MAXIMUM_REFERENCE_COUNT`, and clear provisional PBN-lock bookkeeping.
- Data decrements reject free blocks, reduce shared counts, or transition single/provisional blocks to empty unless a PBN lock requires preserving a provisional reference.
- Block-map increments use `MAXIMUM_REFERENCE_COUNT` to prevent dedupe against block-map blocks. In normal operation they are expected to come from provisional state; rebuild/replay may create them from free state.
- `vdo_adjust_reference_count()` is the normal entry point. It validates slab openness, maps PBN to slab block number, updates the counter, and manages slab-journal lock conversion/release.
- `vdo_adjust_reference_count_for_rebuild()` applies non-normal-operation updates and dirties the affected reference block.
- `vdo_replay_reference_count_change()` skips slab journal entries already reflected in the saved per-sector commit point, otherwise replays and dirties the block.

Free-space management:
- `search_cursor` keeps a per-slab free-search hint.
- `vdo_find_free_block()` scans byte counters using word-sized little-endian reads and a padded counter array.
- `vdo_allocate_unreferenced_block()` finds a zero counter, marks it `PROVISIONAL_REFERENCE_COUNT`, updates free/allocated accounting, and advances the cursor.
- `vdo_provisionally_reference_block()` marks a specific free block provisional and optionally records that on a `pbn_lock`.

Persistence:
- Dirty reference blocks are waiters on `ref_counts->dirty_blocks`.
- `vdo_pack_reference_block()` writes the current slab journal point into every sector and copies the sector’s counters.
- Writes use `REQ_OP_WRITE | REQ_PREFLUSH` so the recovery/slab journal entries covering the reference update are stable before the refcount block reaches disk.
- `finish_reference_block_write()` releases the slab journal block lock associated with that saved reference block and requeues the block if it was dirtied during the write.
- When all dirty/writing work is done, `update_slab_summary_as_clean()` marks the slab clean in the slab summary with the current free-block count.
- Loading unpacks per-sector commit points, warns on torn writes where sector commit points differ, recomputes allocated counts, clears stale provisional references, and recomputes free blocks.

Drain/state behavior:
- `vdo_drain_ref_counts()` chooses load or save behavior based on slab admin state: scrubbing may load saved counts; save-for-scrubbing/rebuilding/saving may dirty and write blocks.
- `vdo_acquire_dirty_block_locks()` dirties all reference blocks and makes them hold lock `1` in the slab journal, used for first-journal initialization.
- I/O errors enter read-only mode through the slab’s read-only notifier.

Dependencies:
- Slab state and PBN translation from `slab.h`.
- Journal positions from `journal-point.h`.
- Slab journal lock operations from `slab-journal.h`.
- Slab summary updates from `slab-summary.h`.
- VIO pool and metadata I/O for async reads/writes.
