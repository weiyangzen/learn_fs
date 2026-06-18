# File Research: sources/cow-pools/bcachefs/fs/bcachefs/alloc/lru_format.h

On-disk LRU key value definitions.

Defines:
- `struct bch_lru`, with generic value header and `idx`.
- `BCH_LRU_TYPES()` list:
  - `read`
  - `fragmentation`
  - `stripes`
- `enum bch_lru_type`.
- Special LRU IDs:
  - `BCH_LRU_BUCKET_FRAGMENTATION`
  - `BCH_LRU_STRIPE_FRAGMENTATION`
- 48-bit time/index encoding limit: `LRU_TIME_BITS` and `LRU_TIME_MAX`.

Purpose:
- Encodes multiple LRU domains in one `BTREE_ID_lru` namespace by storing type in high bits of `bpos.inode` and time/index in low bits.
