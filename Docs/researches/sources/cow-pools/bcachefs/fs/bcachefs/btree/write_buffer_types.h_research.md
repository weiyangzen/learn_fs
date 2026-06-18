# File Research: sources/cow-pools/bcachefs/fs/bcachefs/btree/write_buffer_types.h

This header defines the core write-buffer data structures.

Key types:
- `BCH_WRITE_BUFFER_BTREES()` lists the dense set of write-buffer-enabled btrees.
- `enum bch_wb_btree` gives compact array indices for those btrees.
- `struct wb_key_ref` stores a sortable packed reference made from key position plus darray index.
- `struct btree_write_buffered_key` stores original journal sequence plus a padded bkey.
- `struct btree_write_buffer_keys` owns a darray of variable-sized key records, a journal pin, a mutex, and backrefs identifying the btree and whether this is the flushing side.
- `enum wb_flush_caller` records why a flush was requested.
- `struct bch_fs_btree_write_buffer` is the per-btree state: sorted references, incoming/flushing buffers, flush work item, diagnostics counters, and accounting accumulator array.

Important design:
- The per-btree split avoids storing btree id in each key.
- Accounting keys get a small fixed padded value limit for in-memory accumulation.
- Backrefs let journal-pin callbacks recover the owning buffer from only the pin pointer.
