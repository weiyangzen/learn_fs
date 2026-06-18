# File Research: sources/cow-pools/bcachefs/fs/bcachefs/alloc/background.h

This header exposes helpers and declarations for alloc-background logic.

Bucket helpers:
- `bch2_dev_bucket_exists()` validates a `device:bucket` position.
- `bucket_to_u64()` and `u64_to_bucket()` encode/decode bucket positions for btree indexes.

Generation and data type:
- `BUCKET_GC_GEN_MAX` defines the allowed stale generation window.
- `alloc_gc_gen()` computes generation gap.
- `bucket_data_type()` normalizes cached and stripe data as user data from the bucket perspective.
- `bucket_data_type_mismatch()` checks incompatible bucket/pointer data types.
- `data_type_movable()` identifies btree/user/stripe data as movable.

Sector accounting:
- `bch2_bucket_sectors_total()`, `bch2_bucket_sectors_dirty()`, `bch2_bucket_sectors()`, `bch2_bucket_sectors_fragmented()`, and `bch2_bucket_sectors_unstriped()` compute alloc-key sector quantities.
- `alloc_data_type()` derives the logical bucket state.
- `alloc_data_type_set()` stores that derived state.

Auxiliary indexes:
- `alloc_lru_idx_read()` and `alloc_lru_idx_fragmentation()` compute LRU keys.
- `alloc_freespace_genbits()` and `alloc_freespace_pos()` encode generation bits into freespace positions.
- `alloc_gens_pos()`, `bucket_gens_pos_to_alloc()`, and `alloc_gen()` map between alloc keys and packed bucket generation keys.

Alloc v4/backpointer layout:
- `alloc_v4_u64s_noerror()`, `alloc_v4_u64s()`, `set_alloc_v4_u64s()`, `alloc_v4_backpointers()`, and `alloc_v4_backpointers_c()` compute and access alloc v4 variable trailing inline backpointer storage.
- `bkey_is_alloc()` recognizes legacy alloc key types.

The header declares alloc conversion, validation, text rendering, bkey ops, bucket generation initialization, alloc reading, freespace index updates, trigger entry points, device removal, capacity routines, allocator device add/remove/set-rw operations, and capacity lifecycle functions.
