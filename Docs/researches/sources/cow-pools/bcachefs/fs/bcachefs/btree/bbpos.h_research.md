# File Research: sources/cow-pools/bcachefs/fs/bcachefs/btree/bbpos.h

This small header provides helpers for `struct bbpos`, a combined btree-id plus btree-position cursor.

Key contents:
- `bbpos_cmp()` orders first by btree id, then by `bpos`.
- `bbpos_successor()` advances within the current btree until `SPOS_MAX`, then advances to the next btree and resets position to `POS_MIN`; it BUGs if advanced beyond `BTREE_ID_NR`.
- `bch2_bbpos_to_text()` renders a combined position as `<btree-name>:<bpos>`.

Role:
- Used by cache pinning and GC generation progress tracking where a global position must span multiple btrees, not only positions inside one tree.
