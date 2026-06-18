# File Research: sources/cow-pools/bcachefs-tools/fs/btree/write_buffer.c

Read completeness: full file read, 1488 lines.

Purpose: batching layer for btrees with many small updates, especially accounting, LRU, backpointer, discard, deleted-inode, reconcile, and stripe-backpointer btrees. It moves journaled write-buffer entries into per-btree buffers, sorts and deduplicates them, flushes them to btree leaves with a fast path when possible, and preserves journal ordering with pins and slowpath commits when required.

Major components:
- Compile-time consistency check ensures the dense `BCH_WRITE_BUFFER_BTREES()` list matches all `BTREE_IS_write_buffer` btree ids.
- `wb_key_ref_cmp()`, `wb_key_eq()`, `wb_key_seq_cmp()`, and `wb_sort()` implement compact position/index sorting for buffered keys, including an x86_64 carry-chain comparator.
- `wb_flush_one()` traverses to the target leaf, optionally accumulates accounting deltas into an existing accounting key, takes a write lock, prepares the node for write, fast-inserts if the key fits, and schedules merge work if needed.
- `wb_flush_one_slowpath()` drops the leaf write lock and commits one key using the original journal sequence and reclaim-safe/no-journal-reservation flags.
- `btree_write_buffered_insert()` stages a write-buffered key into a transaction without re-journaling it, preserving original recovery order.
- Buffer management helpers resize darrays, move keys from `inc` to `flushing`, update/drop journal pins, and trigger journal watermark recalculation when low-on-write-buffer pressure clears.
- `wb_flush_sorted_range()` flushes one sorted slice with its own transaction and iterator, counting fast/noop/slowpath outcomes.
- `wb_flush_sorted_sharded()` splits large sorted arrays into CPU-bounded shards on `write_buffer_shard_wq`, joins with closures, and aggregates errors/counters.
- `bch2_btree_write_buffer_flush_locked()` is the main per-btree flush: moves intake keys, builds `wb->sorted`, sorts by position, deduplicates adjacent same-position runs, accumulates accounting duplicates, runs sharded fastpath, and then slowpath flushes remaining keys in journal sequence order.
- Journal intake helpers lock every per-btree instance in ascending order, convert `BCH_JSET_ENTRY_write_buffer_keys` to buffered entries, manage accounting accumulator arrays, pin non-empty buffers, and unlock/queue flush/resize work.
- `fetch_wb_keys_from_journal()` pulls pending write-buffer journal buffers up to a target sequence.
- Sync flush dispatch `btree_write_buffer_flush_seq()` fetches journal keys, queues all per-btree workers with pins at or below the target sequence, and waits for `write_buffer_flush_wait`.
- Journal pin callback `bch2_btree_write_buffer_journal_flush()` queues the owning per-btree flush worker.
- Public flush surfaces include `bch2_btree_write_buffer_flush_sync()`, `bch2_btree_write_buffer_flush_going_ro()`, `bch2_btree_write_buffer_tryflush()`, and `bch2_btree_write_buffer_maybe_flush()`.
- Lifecycle/stat helpers include flush worker function, accounting slowpath insertion, journal key slowpath insertion, resize, text reporting, stop/start, early init, full init, and exit.

Control-flow and invariants:
- The write buffer has per-btree `inc` and `flushing` buffers. Intake goes to `inc` unless `flushing` is locked and has room; flushing workers drain `flushing` and opportunistically move `inc`.
- Journal pins are attached when keys enter buffers and only dropped after the relevant buffered keys are flushed or retained for a later accounting-replay pass.
- Same-position dedup runs before sharding so no duplicate key run can straddle shard boundaries and flush out of order.
- Accounting keys are deltas. Duplicate accounting keys are accumulated, and accounting flushing is deferred until `BCH_FS_accounting_replay_done` when necessary.
- Fastpath leaf insertion does not re-journal the key; slowpath commits use `BCH_TRANS_COMMIT_no_journal_res` with `trans->journal_res.seq` set to the original buffered sequence.
- Flush workers drain everything once queued, not just threshold-triggered work, and wake sync flush waiters afterward.

Dependencies and integration:
- Depends on accounting accumulation, btree locking/update/interior helpers, extents, journal read/reclaim, counters, enumerated write refs, workqueues, sorting, closures, and transaction restart handling.
- Public inline helpers and declarations live in `write_buffer.h`; data structures live in `write_buffer_types.h`.
- Integrated with journal replay/read paths by converting journal entries from write-buffer form back to normal btree keys once staged.

Risks and validation notes:
- Ordering is the central correctness risk: re-journaling buffered keys or flushing same-position duplicates out of order can make crash recovery replay the wrong value.
- Memory pressure can force partial moves from `inc` to `flushing`; pin updates must match the first remaining sequence in each buffer.
- Accounting replay deferral is a special case that can leave keys in `flushing`; compaction keeps only non-zero live deltas.
- The x86_64 comparator is checked against the generic comparator under `EBUG_ON`, but any layout change to `struct wb_key_ref` must preserve its assumptions.
