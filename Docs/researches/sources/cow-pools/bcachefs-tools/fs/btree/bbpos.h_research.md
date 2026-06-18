# File Research: sources/cow-pools/bcachefs-tools/fs/btree/bbpos.h

## Purpose
Provides helpers for `struct bbpos`, a combined btree-id plus btree-position cursor.

## Main Functions
- `bbpos_cmp(l, r)`: orders first by `btree`, then by `bpos_cmp()`.
- `bbpos_successor(pos)`: advances within the current btree position until `SPOS_MAX`, then moves to the next btree and resets position to `POS_MIN`.
- `bch2_bbpos_to_text(out, pos)`: prints `btree_id:bpos`.

## Dependencies
- `bbpos_types.h` for `struct bbpos`.
- `bkey_methods.h` for `bch2_bpos_to_text()`.
- `cache.h` for `bch2_btree_id_to_text()`.

## Notable Details
- `bbpos_successor()` uses `BUG()` if it cannot advance.
- The successor logic can produce a one-past-known btree id when called at the last btree’s `SPOS_MAX`, because it checks `pos.btree != BTREE_ID_NR` before incrementing. That may be intentional sentinel behavior, but callers must not assume the result is always within `0..BTREE_ID_NR - 1`.
