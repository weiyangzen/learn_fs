# File Research: sources/cow-pools/bcachefs/fs/bcachefs/alloc/discard.c

Implements bcachefs discard/TRIM processing and cached-bucket invalidation. It operates over `BTREE_ID_need_discard`, alloc keys, LRU keys, backpointers, per-device discard queues, and filesystem/device write refs.

Key responsibilities:
- Track in-flight discard bios in `c->discards.in_flight`, with per-device and global ref counters.
- Submit `REQ_OP_DISCARD` bios for buckets whose alloc state is `BCH_DATA_need_discard`.
- After IO completion, mark alloc keys back to `BCH_DATA_free` in the alloc btree.
- Enforce journal safety: buckets are not freed for reuse until `journal_seq_empty` is flushed and older than rewind limits.
- Compute per-device discard release pressure and advance journal rewind sequence when free-space pressure requires it.
- Provide async normal discard work and fast per-device discard work.
- Invalidate cached buckets by walking LRU entries, resolving backpointers, dropping a removed/evicted device from referenced extents, and setting unrecoverable error keys if no readable pointer remains.
- Initialize and tear down discard/invalidations work items, bioset, and dynamic arrays.

Important control flow:
- `bch2_do_discards()` iterates `BTREE_ID_need_discard`, calls `bch2_discard_one_bucket()`, drains completed bios via `bch2_discards_complete()`, then may flush the journal/write buffer and retry.
- `bch2_discard_one_bucket()` performs eligibility checks: nouse bucket, duplicate in-flight discard, journal flush state, rewind state, data type, open bucket, device writable ref, hardware discard availability, and `opts.nochanges`.
- `__discard_mark_free()` is the committed state transition from `need_discard` to `free`; it also clears compatibility discard flags and emits trace events.
- Fast discard queues buckets from just-closed open buckets via `bch2_fast_discard_bucket_add()`.
- Invalidation starts at LRU entries, confirms alloc key consistency, scans backpointers, and mutates referenced keys to remove the target device.

Concurrency and lifetime:
- `c->discards.lock` protects in-flight discard entries and ref counters.
- Device write refs pin devices until both discard IO and alloc-btree mark-free commits are complete.
- Work is scheduled on `c->write_ref_wq` and guarded by enumerated filesystem write refs.
- Comments explicitly call out a race avoided between device removal and `discards_complete()` by holding `io_ref` through alloc updates.

Dependencies:
- Alloc key conversion/update helpers, btree iterators, write buffer flushing, journal flush/rewind APIs, device usage accounting, LRU helpers, backpointer helpers, and trace events.

Failure behavior:
- Unexpected post-discard alloc type mismatch in `__discard_mark_free()` triggers emergency read-only.
- Normal races from the write buffer are counted as `bad_data_type`.
- EROFS errors are suppressed at worker exit; other errors are logged.
