# File Research: sources/cow-pools/bcachefs-tools/fs/alloc/lru.c

Implements LRU key validation, text rendering, LRU update helpers, LRU consistency checks, and device-removal cleanup.

Key responsibilities:
- Validate LRU keys, currently rejecting entries at time zero.
- Render LRU values and encoded LRU positions.
- Add/remove buffered `BTREE_ID_lru` set keys.
- Change LRU position atomically by clearing old position and setting new position.
- Check that alloc or stripe keys have matching LRU entries.
- Remove LRU entries associated with a removed device.
- Full fsck-style scan of the LRU btree with write-buffer flush assistance and progress reporting.

Important logic:
- `__bch2_lru_set()` uses `bch2_btree_bit_mod_buffered()` for buffered set/clear operations.
- `bch2_lru_check_set()` repairs missing LRU entries when the referring alloc/stripe key expects one.
- `lru_pos_to_bp()` maps LRU key type to the btree/key that should justify the LRU entry:
  - read and bucket-fragmentation LRUs point to alloc keys.
  - stripe-fragmentation LRUs point to stripe keys.
- `bkey_lru_type_idx()` recomputes the expected LRU time from alloc read time, alloc fragmentation, or stripe LRU position.
- `bch2_check_lru_key()` removes incorrect LRU entries after reporting fsck errors.
- `bch2_check_lrus()` scans all LRU keys and commits repairs with `BCH_TRANS_COMMIT_no_enospc`.

Dependencies:
- Alloc conversion helpers, btree buffered updates, btree write buffer flush helpers, EC stripe LRU helpers, fsck/progress infrastructure, and recovery/error code support.
