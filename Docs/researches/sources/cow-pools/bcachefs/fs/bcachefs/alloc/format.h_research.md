# File Research: sources/cow-pools/bcachefs/fs/bcachefs/alloc/format.h

On-disk allocation metadata formats.

Defines historical and current alloc key formats:
- `struct bch_alloc` plus V1 packed field list.
- `struct bch_alloc_v2`.
- `struct bch_alloc_v3` with journal sequence and flags.
- `struct bch_alloc_v4`, the current per-bucket allocation state.
- `struct bch_bucket_gens`, packed generation array for 256 buckets.

Important `bch_alloc_v4` fields:
- `journal_seq_nonempty` and `journal_seq_empty` track empty/nonempty transitions for noflush and discard safety.
- `flags` retains compatibility flags such as `NEED_DISCARD` and `NEED_INC_GEN`.
- `gen`, `oldest_gen`, and `data_type` describe bucket generation and allocation state.
- Sector counters: dirty, cached, stripe sectors.
- `io_time[2]` supports read/write LRU accounting.
- Stripe and backpointer counts support EC and backpointer metadata.

Key comment:
- Empty-state transitions are explicit:
  - nonempty to empty becomes `BCH_DATA_need_discard`.
  - `need_discard` to reusable empty becomes `BCH_DATA_free`.
  - high generation pressure can become `BCH_DATA_need_gc_gens`.
- `NEED_DISCARD` is maintained for compatibility but no longer drives `alloc_data_type()`.

Dependencies:
- Included by `bcachefs_format.h` to define `KEY_TYPE_alloc_v*` values and alloc btree payload layout.
