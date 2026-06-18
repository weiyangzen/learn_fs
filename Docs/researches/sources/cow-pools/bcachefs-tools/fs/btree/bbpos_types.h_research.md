# File Research: sources/cow-pools/bcachefs-tools/fs/btree/bbpos_types.h

## Purpose
Defines the compact type used to identify an ordered position across all btrees.

## Main Contents
- `struct bbpos`:
  - `enum btree_id btree`
  - `struct bpos pos`
- `BBPOS(btree, pos)` inline constructor.
- Boundary macros:
  - `BBPOS_MIN`: btree `0`, `POS_MIN`
  - `BBPOS_MAX`: btree `BTREE_ID_NR - 1`, `SPOS_MAX`

## Role In System
Used by btree-cache pinning and any logic that needs an ordered global cursor over `(btree id, key position)`.
