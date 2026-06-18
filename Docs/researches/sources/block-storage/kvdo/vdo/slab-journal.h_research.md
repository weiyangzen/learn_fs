# File Research: sources/block-storage/kvdo/vdo/slab-journal.h

Declares the slab journal runtime structure and public operations.

Important types:
- `struct journal_lock`: per-slab-journal-block lock count plus the recovery-journal block sequence that lock protects.
- `struct slab_journal`: owns waiters, entry queue, parent slab, state flags, sequence numbers, recovery lock, entry capacities, recovery journal pointer, summary zone pointer, statistics, outstanding write list, current packed tail block, thresholds, dirty-list entry, reap pointer, and flexible array of journal locks.

Inline helpers:
- `vdo_pack_slab_journal_entry()` packs a slab block number and increment bit.
- `vdo_unpack_slab_journal_block_header()` decodes packed header fields and recovery point.
- `vdo_get_slab_journal_block_offset()` maps sequence numbers to ring offsets.

Public API:
- Construction/destruction and state: `vdo_make_slab_journal()`, `vdo_free_slab_journal()`, `vdo_is_slab_journal_blank()`, `vdo_is_slab_journal_active()`.
- Waiter/reopen/replay: `vdo_abort_slab_journal_waiters()`, `vdo_reopen_slab_journal()`, `vdo_attempt_replay_into_slab_journal()`.
- Normal operation: `vdo_add_slab_journal_entry()`, `vdo_adjust_slab_journal_block_reference()`, `vdo_release_recovery_journal_lock()`.
- Lifecycle: `vdo_drain_slab_journal()`, `vdo_decode_slab_journal()`, `vdo_resume_slab_journal()`.
- Recovery policy: `vdo_slab_journal_requires_scrubbing()`.
- Diagnostics: `vdo_dump_slab_journal()`.

This header is central to interactions among slabs, refcounts, recovery journal, block allocators, and slab summary.
