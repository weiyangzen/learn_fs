# File Research: sources/block-storage/kvdo/vdo/slab-scrubber.c

Implements slab scrubbing for unrecovered slabs. Scrubbing reads a slab’s journal, replays relevant entries into refcounts, saves rebuilt refcount blocks, and moves to the next queued slab.

Construction:
- `vdo_make_slab_scrubber()` allocates the scrubber, a multi-block metadata VIO, and a buffer large enough for one full slab journal.
- The scrubber starts suspended and has two slab queues: high-priority and normal.

Queueing:
- `vdo_register_slab_for_scrubbing()` removes the slab from allocator queues, increments scrubber slab count once, records that it was queued, and enqueues it on high-priority or normal list.
- High-priority mode is used when journal pressure requires urgent recovery before more entries can be admitted.

Scrub flow:
- `vdo_scrub_slabs()` prepares the scrubber completion and starts `scrub_next_slab()`.
- `scrub_next_slab()` notifies clean-slab waiters, handles read-only/drain/empty cases, selects the next slab, and starts a slab action in `VDO_ADMIN_STATE_SCRUBBING`.
- `start_scrubbing()` skips journal replay if the slab summary says the slab is clean; otherwise it reads the whole slab journal.
- `apply_journal_entries()` determines journal `head` from the last/tail block, validates every block from head to tail, replays entries, and then starts `VDO_ADMIN_STATE_SAVE_FOR_SCRUBBING` so rebuilt refcounts are persisted.
- `slab_scrubbed()` marks the slab finished, decrements slab count, and continues.

Replay validation:
- Each journal block must match nonce, metadata type, expected sequence number, and entry capacity constraints.
- `apply_block_entries()` decodes entries and rejects out-of-range slab block numbers.
- Entries are applied through `vdo_replay_reference_count_change()`, which skips changes already represented by saved refcount commit points.

Control API:
- `vdo_scrub_high_priority_slabs()` optionally promotes at least one normal slab, then scrubs only high-priority slabs.
- `vdo_stop_slab_scrubbing()` drains/suspends after the current slab.
- `vdo_resume_slab_scrubbing()` resumes if slabs remain.
- `vdo_enqueue_clean_slab_waiter()` lets callers wait for a clean slab while scrubber is active.

Failure:
- Metadata read errors and corrupt journal validation enter read-only mode and complete with the error.
