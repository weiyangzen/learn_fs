# File Research: sources/cow-pools/bcachefs-tools/fs/alloc/lru.h

Public LRU helper header.

Defines:
- `lru_pos_id()` and `lru_pos_time()` for decoding LRU positions.
- `lru_pos()` for encoding an LRU ID, device/bucket payload, and time into `struct bpos`.
- `lru_start()` / `lru_end()` bounds helpers.
- `lru_type()` mapping special LRU IDs to read, bucket-fragmentation, or stripe-fragmentation LRUs.
- `bch2_bkey_ops_lru` with validation/text callbacks and minimum value size.
- `bch2_lru_change()` wrapper that avoids work when the time is unchanged.

Exports:
- LRU validation/text helpers.
- LRU change helper.
- Device LRU cleanup.
- Missing-entry check/repair helper.
- Full LRU check entry point.

Role:
- Used by alloc triggers, discard invalidation, cached bucket eviction, stripe fragmentation tracking, and fsck validation.
