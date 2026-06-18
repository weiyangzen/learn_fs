# File Research: sources/block-storage/kvdo/vdo/slab-journal.c

Implements the per-slab journal that records reference-count updates before applying/persisting them safely. It coordinates recovery-journal locks, slab summary tail updates, dirty refcount flush pressure, ring reaping, replay insertion, and normal data-VIO admission.

State model:
- `head`: oldest journal block on disk.
- `unreapable`: oldest block that cannot yet be reaped.
- `tail`: sequence number after the active journal interval.
- `next_commit`: oldest uncommitted write, or tail when none.
- `summarized`/`last_summarized`: tail positions recorded in slab summary.
- `recovery_lock`: recovery-journal block currently held by a dirty tail block.
- Per-block `journal_lock` entries track lock counts and recovery-journal start block.
- `uncommitted_blocks` tracks outstanding tail-block writes.
- `entry_waiters` queues data VIOs waiting to append entries.

Creation:
- `vdo_make_slab_journal()` sizes the journal from `slab_config`, initializes thresholds, statistics, summary pointer, recovery journal pointer, packed block buffer, dirty list entries, nonce/metadata header, and sequence state.
- `flushing_deadline` is normally just before the blocking threshold, leaving time to write refcount blocks before blocking.

Appending:
- `vdo_add_slab_journal_entry()` validates slab/open/read-only state, queues the `data_vio`, optionally registers unrecovered slabs for high-priority scrubbing, and calls `add_entries()`.
- `add_entries()` processes waiters in order so slab journal order matches recovery journal order.
- It stops adding entries during partial writes, rebuild, tail commit wait, blocking threshold, or full on-disk journal lock conditions.
- First entry in a new tail block:
  - acquires recovery-journal block reference,
  - marks the slab journal dirty in allocator order by recovery lock,
  - initializes journal block lock count,
  - may dirty all refcount blocks for the first-ever block.
- `add_entry_from_waiter()` appends the journal entry and then calls `vdo_modify_slab_reference_count()` with the slab journal point for that entry.

Writing and committing:
- `commit_tail()` writes a non-empty tail unless read-only or already waiting.
- Before writing, it removes the journal from the allocator dirty list because the recovery journal no longer needs to force that in-progress tail to commit.
- `write_slab_journal_block()` packs the header, copies the block to a VIO, adjusts unused per-entry locks for partial blocks, submits metadata write, advances `tail`, and reinitializes the in-memory tail block.
- `complete_write()` updates write statistics, advances `next_commit`, and triggers slab-summary tail update.

Slab summary and lock release:
- `update_tail_block_location()` writes the committed tail offset, dirty/clean status, load-refcounts flag, and free-block hint to the slab summary.
- `release_journal_locks()` runs after summary write, releases corresponding recovery-journal references and slab-journal block locks, then tries reaping and further summary updates.

Reaping:
- `reap_slab_journal()` advances `unreapable` while old journal blocks have no locks.
- It always issues a lower-layer flush before setting `head = unreapable`, preventing reference-block writes from being lost before overwriting old journal blocks.
- Lock decrement through `vdo_adjust_slab_journal_block_reference()` may trigger reaping.

Recovery/replay:
- `vdo_attempt_replay_into_slab_journal()` accepts only recovery points newer than the current tail header’s recovery point. It may commit a full tail first and wait for recovery if necessary.
- If the ring would overrun, replay advances `head`/`unreapable` because the old head must already have been reaped before crash.
- `vdo_decode_slab_journal()` reads the summarized tail block, validates nonce/type, restores `tail`, `head`, and tail header, or skips impossible default summary states.
- `vdo_slab_journal_requires_scrubbing()` checks journal length against scrubbing threshold.

Drain/resume:
- `vdo_drain_slab_journal()` commits the tail for most drain modes, but skips rebuilding, suspending, and save-for-scrubbing.
- `vdo_resume_slab_journal()` reopens/reset journals after successful save.
- `vdo_abort_slab_journal_waiters()` aborts queued VIOs with read-only errors.

Failure behavior:
- Metadata write/flush errors are recorded and force VDO read-only mode.
- Waiters are aborted after read-only transition.
