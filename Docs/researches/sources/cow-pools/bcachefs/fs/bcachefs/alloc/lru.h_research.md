# File Research: sources/cow-pools/bcachefs/fs/bcachefs/alloc/lru.h

LRU helper header.

Defines:
- `lru_pos_id()` and `lru_pos_time()` for decoding the 64-bit inode field into LRU ID and time.
- `lru_pos()`, `lru_start()`, and `lru_end()` for constructing btree positions.
- `lru_type()` mapping special LRU IDs to read, fragmentation, or stripe LRU types.
- Bkey ops for `KEY_TYPE_lru`.
- Inline wrapper `bch2_lru_change()` that avoids work when old and new times match.

Exports:
- LRU validation/text helpers.
- LRU position rendering.
- LRU change, device removal, check/set, and full check functions.

Role:
- Shared by allocator/discard invalidation and fsck consistency checks for cached buckets, fragmentation ordering, and stripe cache ordering.
