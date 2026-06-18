# File Research: sources/cow-pools/bcachefs/fs/bcachefs/btree/sort.h

This header declares B-tree sorting and compaction APIs.

Key definitions:
- `struct sort_iter` and `struct sort_iter_stack` hold multiple bset key ranges for merge-sort style processing.
- `sort_iter_add()` appends a non-empty key range.
- Sorting APIs cover read-time overlap repair, repacking, writeback sorting with unwritten whiteouts, and ordinary deleted-key filtering.
- Whiteout APIs support marking, sorting, dropping, lazy compaction, and full compaction.
- Node APIs support sorting selected bset ranges, sorting into another node, compacting a node, and rebuilding auxiliary search trees.

Important policy:
- Lazy whiteout compaction triggers when dead key space is both large and a substantial fraction of a bset.
- `should_compact_all()` uses a geometric-size heuristic to decide if `MAX_BSETS` should collapse to fewer sets.
