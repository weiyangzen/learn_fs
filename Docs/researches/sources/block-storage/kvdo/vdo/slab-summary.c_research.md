# File Research: sources/block-storage/kvdo/vdo/slab-summary.c

Implements the slab summary: a per-zone persisted table of compact per-slab state used for journal recovery, refcount loading, cleanliness, and free-space hints.

Fullness hints:
- `compute_fullness_hint()` compresses free-block count using `summary->hint_shift`, preserving nonzero free counts as at least `1`.
- `get_approximate_free_blocks()` expands the hint back to an approximate free count.

Construction:
- `vdo_make_slab_summary()` skips allocation for formatter use when no partition is supplied.
- Otherwise it allocates a `struct slab_summary` with one zone per physical zone, allocates all entries for all possible zones/slabs, initializes default entries, sets partition origin, and creates `slab_summary_block` objects with metadata VIOs.
- Default entries use tail block offset `0`, full free-space hint, `load_ref_counts = false`, and clean state.

Writing:
- Each `slab_summary_block` has current and next waiter queues plus a write VIO.
- `vdo_update_slab_summary_entry()` updates the in-memory entry, preserving `load_ref_counts` once set, queues the caller waiter, and launches a block write.
- `launch_write()` batches all pending waiters for the block, copies entries to an outgoing buffer, and submits `REQ_OP_WRITE | REQ_PREFLUSH`.
- The preflush ensures slab journal tail blocks and reference updates covered by the summary update are stable.
- Completion notifies current waiters with success or read-only status, clears writing state, and launches queued next updates if present.
- Write errors record metadata I/O failure and enter read-only mode.

Drain/resume:
- `vdo_drain_slab_summary_zone()` starts admin draining and completes when no writes remain.
- `vdo_resume_slab_summary_zone()` resumes a quiescent summary zone.

Read/query API:
- Tail offset: `vdo_get_summarized_tail_block_offset()`.
- Refcount load flag: `vdo_must_load_ref_counts()`.
- Cleanliness: `vdo_get_summarized_cleanliness()`.
- Approximate free count: `vdo_get_summarized_free_block_count()`.
- Per-slab statuses for allocator selection: `vdo_get_summarized_slab_statuses()`.

Loading/combining:
- `vdo_load_slab_summary()` creates a multi-block VIO over the whole summary partition.
- Formatting and loading-for-rebuild skip disk read and immediately use initialized/default data.
- Normal load reads all zone summaries, then `combine_zones()` merges old per-zone layouts into zone 0 and copies the combined summary to every zone region.
- The combined summary is written back to disk, then load completes.
- `zones_to_combine` supports old persisted zone counts during load.

Statistics:
- `vdo_get_slab_summary_statistics()` returns cumulative blocks written from an atomic counter.
