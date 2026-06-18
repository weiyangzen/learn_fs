# File Research: sources/cow-pools/bcachefs/fs/bcachefs/btree/write_buffer.c

This file implements the B-tree write buffer: a batching layer for btrees that receive many small updates, such as backpointers, LRU, discard, reconcile, stripe backpointers, deleted inodes, and accounting.

Key flow:
- Journal entries of type `BCH_JSET_ENTRY_write_buffer_keys` are fetched and staged into per-btree write-buffer instances.
- Each per-btree buffer has incoming (`inc`) and flushing buffers, both journal-pinned.
- Intake eagerly locks all per-btree buffers in ascending index order, accumulates accounting deltas, and adds journal pins.
- Flush moves incoming keys to the flushing buffer, builds compact key-position references, sorts them, collapses duplicate positions, and accumulates accounting duplicates.
- Fast path traverses the target leaf once per key range, keeps a write lock while keys stay in the same leaf, and inserts directly when the key fits.
- Slow path commits in journal sequence order when fast insertion would deadlock reclaim, when the key does not fit, or when accounting replay is not ready.
- Large sorted flushes shard across CPUs using a separate shard workqueue.
- Sync flushers fetch journal keys up to a target sequence, queue all relevant per-btree workers, and wait for pins at or below that sequence.
- Journal pin callbacks only queue the appropriate per-btree worker; they do not perform flushes inline.
- Startup/init allocate per-btree arrays and workqueues; exit asserts no buffered keys remain unless the journal is in error.

Important invariants:
- Write-buffer btree list is compile-time checked against `BTREE_IS_write_buffer` flags.
- Once a key enters the write buffer, it must flush using its original journal sequence to preserve recovery order.
- Duplicate same-position entries must be collapsed before sharded flush so older updates cannot race newer updates across shard boundaries.
- Accounting updates are deltas, so duplicates are accumulated rather than overwritten.
- `inc.pin` and `flushing.pin` ordering uses acquire/release care so sync flushers do not miss in-flight pins.

Dependencies include B-tree locking/update/interior APIs, journal read/reclaim, accounting accumulation, closure work, workqueues, Eytzinger sorting, and transaction restart handling.
