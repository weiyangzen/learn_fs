# File Research: sources/cow-pools/bcachefs/fs/bcachefs/btree/write_buffer.h

This header exposes write-buffer indexing, intake, flush, accounting, diagnostics, lifecycle, and helper APIs.

Key elements:
- `bch_wb_btree_idx()` maps write-buffer-enabled `btree_id` values to dense `enum bch_wb_btree` indices.
- `bch_wb_btree_to_btree_id()` maps back to real B-tree IDs.
- Flush pressure helpers check per-btree and global buffer fullness.
- Public flush APIs cover sync flush, going-read-only flush, tryflush, and maybe-flush for check/repair code.
- `wb_maybe_flush` tracks the last key that triggered a repair-time flush to prevent repeated useless flushes.
- `journal_keys_to_wb` batches one journal buffer’s keys across all per-btree buffers.
- Accounting helpers use an Eytzinger-sorted accumulator array for fast delta coalescing.
- Write-buffered key iteration helpers treat the underlying darray as variable-sized records.

Important invariants:
- Buffered key entries do not store a btree id because the containing write buffer implies it.
- `wb_key_u64s()` includes the journal-sequence header plus the actual bkey.
- Journal intake reserves room per btree and falls back to slowpath when the selected buffer lacks capacity.
