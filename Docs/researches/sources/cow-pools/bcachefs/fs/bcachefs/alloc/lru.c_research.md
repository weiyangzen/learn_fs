# File Research: sources/cow-pools/bcachefs/fs/bcachefs/alloc/lru.c

Implements LRU key validation, display, mutation, device removal cleanup, and fsck checking.

Key responsibilities:
- Validate LRU entries, currently rejecting time zero.
- Render LRU values and positions.
- Add/remove LRU set keys through the btree write buffer.
- Update LRU entries with `__bch2_lru_change()`.
- Remove alloc-related LRU entries for a device during device removal.
- Verify LRU btree consistency against the referenced alloc or stripe key.
- Repair missing or incorrect LRU entries through fsck error handling.

Important behavior:
- `lru_pos_to_bp()` maps LRU entries back to the referenced btree:
  - read and fragmentation LRUs reference alloc keys by device bucket.
  - stripe LRU references stripe keys.
- `bkey_lru_type_idx()` computes the expected LRU time/index from alloc or stripe metadata.
- `bch2_check_lru_key()` compares actual LRU position time with expected index and deletes bad entries if fsck elects repair.
- `bch2_lru_check_set()` checks that a referring key has its expected LRU set entry and can create it during repair.
- `bch2_check_lrus()` walks the whole LRU btree with progress reporting and write-buffer maybe-flush support.

Dependencies:
- Alloc conversion helpers, btree iter/update/write buffer, EC stripe trigger helpers, recovery/progress helpers, and fsck error framework.
