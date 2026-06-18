# File Research: sources/cow-pools/bcachefs-tools/fs/alloc/background.h

This header exposes allocator background helpers, alloc key operations, and bucket-state derivation logic.

Bucket position helpers:
- `bch2_dev_bucket_exists()` checks whether a `(dev,bucket)` position maps to an existing bucket.
- `bucket_to_u64()` and `u64_to_bucket()` encode/decode bucket positions for auxiliary indexes.

Generation and data-type helpers:
- `BUCKET_GC_GEN_MAX` is the allowed generation gap before a bucket needs GC-gens.
- `alloc_gc_gen()` computes `gen - oldest_gen`.
- `bucket_data_type()` normalizes cached and stripe to user for bucket-type compatibility.
- `bucket_data_type_mismatch()` detects incompatible live data types in the same bucket.
- `data_type_movable()` marks btree, user, and stripe as movable data types.

Sector helpers:
- `bch2_bucket_sectors_total()`, `bch2_bucket_sectors_dirty()`, `bch2_bucket_sectors()`, `bch2_bucket_sectors_fragmented()`, and `bch2_bucket_sectors_unstriped()` derive accounting quantities from `bch_alloc_v4`.

State derivation:
- `alloc_data_type()` derives bucket state from stripe refcount, dirty/stripe sectors, cached sectors, sticky need-discard, and generation gap.
- `alloc_data_type_set()` writes the derived state back to the alloc key.

Auxiliary btree helpers:
- `alloc_lru_idx_read()` and `alloc_lru_idx_fragmentation()` compute LRU keys.
- `alloc_freespace_genbits()` and `alloc_freespace_pos()` encode generation bits into freespace positions.
- `alloc_gens_pos()` and `bucket_gens_pos_to_alloc()` map alloc buckets to packed bucket-gens keys.

Alloc v4 helpers:
- `alloc_v4_u64s_noerror()`, `alloc_v4_u64s()`, `set_alloc_v4_u64s()`, and `alloc_v4_backpointers()` describe alloc v4 value sizing and inline backpointer location.
- Declares bkey ops for alloc v1-v4 and bucket-gens.

Role:
- This is the shared inline contract for allocation triggers, freespace checking, bucket generation maintenance, LRU updates, and capacity/device allocator state.
