# File Research: sources/cow-pools/bcachefs/fs/bcachefs/btree/write.h

This header defines the B-tree writeback interface.

Key elements:
- `struct btree_write_bio`: write work item with copied btree pointer key, bounce data, byte/sector offsets, timing, optional async-object index, and embedded `bch_write_bio`.
- Write flags for “only if need” and “already started”.
- Declarations for node write submission, transaction-aware write, initializing the next bset, post-write cleanup, write stats rendering, flushing all writes, and cancelling writes.

This is consumed by cache, update/commit, node writeback, shutdown, and diagnostic paths.
