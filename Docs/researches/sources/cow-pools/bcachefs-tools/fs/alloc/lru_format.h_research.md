# File Research: sources/cow-pools/bcachefs-tools/fs/alloc/lru_format.h

On-disk LRU format header.

Defines:
- `struct bch_lru`, an obsolete key value containing an `idx`.
- `BCH_LRU_TYPES()` and `enum bch_lru_type`:
  - read
  - fragmentation
  - stripes
- Special LRU IDs:
  - `BCH_LRU_BUCKET_FRAGMENTATION`
  - `BCH_LRU_STRIPE_FRAGMENTATION`
- LRU time encoding constants:
  - `LRU_TIME_BITS = 48`
  - `LRU_TIME_MAX`

Role:
- Provides the encoded key-space layout used by `BTREE_ID_lru`.
- Current LRU presence is represented primarily by `KEY_TYPE_set` keys in the LRU btree.
