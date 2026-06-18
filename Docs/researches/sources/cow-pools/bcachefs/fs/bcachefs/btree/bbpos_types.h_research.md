# File Research: sources/cow-pools/bcachefs/fs/bcachefs/btree/bbpos_types.h

This header defines the `bbpos` data type.

Key contents:
- `struct bbpos` contains `enum btree_id btree` and `struct bpos pos`.
- `BBPOS()` constructs a value.
- `BBPOS_MIN` starts at btree 0 and `POS_MIN`.
- `BBPOS_MAX` ends at `BTREE_ID_NR - 1` and `SPOS_MAX`.

Role:
- Provides a compact cross-btree cursor type for code that needs monotonic ordering across btree spaces, especially GC and cache pinning ranges.
