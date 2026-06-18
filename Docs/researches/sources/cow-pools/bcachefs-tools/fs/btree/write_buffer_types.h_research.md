# File Research: sources/cow-pools/bcachefs-tools/fs/btree/write_buffer_types.h

Read completeness: full file read, 128 lines.

Purpose: shared data structures for the btree write-buffer subsystem.

Key definitions:
- `BCH_WRITE_BUFFER_BTREES()` lists the dense subset of btrees that use write buffering: accounting, lru, need_discard, backpointers, deleted_inodes, reconcile variants, physical reconcile variants, and stripe_backpointers.
- `enum bch_wb_btree` generates dense indexes and `BCH_WB_BTREE_NR`.
- `BTREE_WRITE_BUFERED_VAL_U64s_MAX` caps inline value size for accounting buffered keys.
- `struct wb_key_ref` is a compact sort reference containing a buffer index plus serialized `struct bpos` bytes, overlaid with three 64-bit words for fast comparison.
- `struct btree_write_buffered_key` stores the original journal sequence and padded key payload.
- `struct btree_write_buffer_keys` owns a raw `darray_u64`, a journal pin, a mutex, and back-references identifying which btree and whether this is the flushing buffer.
- `WB_FLUSH_CALLERS()` and `enum wb_flush_caller` classify flush sources for diagnostics: thread, journal pin, sync, maybe, and tryflush.
- `struct bch_fs_btree_write_buffer` owns per-btree write-buffer state: filesystem/index backrefs, sorted refs, `inc` and `flushing` key arrays, flush work, caller, counters, shard stats, and accounting accumulator array.

Dependencies and integration:
- Includes Linux workqueue, darray, and journal pin types.
- Embedded as an array in `struct bch_fs_btree` from `types.h`.
- Consumed by `write_buffer.c` and `write_buffer.h`.

Risks and validation notes:
- The dense btree list must stay synchronized with `BCH_BTREE_IDS()` flags; `write_buffer.c` has a static assertion for this.
- `wb_key_ref` layout depends on endianness and `struct bpos` size; comparator code assumes the index occupies the low bits excluded by same-position equality.
- The macro name `BTREE_WRITE_BUFERED_VAL_U64s_MAX` is misspelled as "BUFERED" in the source and must be referenced exactly.
