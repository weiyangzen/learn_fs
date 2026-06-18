# File Research: sources/cow-pools/bcachefs-tools/fs/btree/sort.h

Read completeness: full file read, 113 lines.

Purpose: public declarations and small inline helpers for btree bset sorting and compaction.

Key definitions:
- `struct sort_iter` stores a target btree, used/size counts, and an array of sorted key ranges.
- `struct sort_iter_stack` provides stack storage for `MAX_BSETS + 1` ranges.
- `sort_iter_init()`, `sort_iter_stack_init()`, and `sort_iter_add()` initialize and populate the merge iterator.
- `enum compact_mode` distinguishes lazy whiteout compaction from complete compaction.
- `should_compact_bset_lazy()` and `bch2_maybe_compact_whiteouts()` encode the lazy dead-key threshold.
- `should_compact_all()` decides whether a node with `MAX_BSETS` should be sorted down to one bset based on the middle bset's size.

Declared API:
- Sorting/repacking: `bch2_key_sort_fix_overlapping()`, `bch2_sort_repack()`, `bch2_sort_keys_keep_unwritten_whiteouts()`, and `bch2_sort_keys()`.
- Bounce buffers: `bch2_btree_bounce_alloc()` and `bch2_btree_bounce_free()`.
- Whiteouts/compaction: `bch2_set_bset_needs_whiteout()`, `bch2_sort_whiteouts()`, `bch2_drop_whiteouts()`, `bch2_compact_whiteouts()`, `bch2_btree_node_sort()`, `bch2_btree_sort_into()`, `bch2_btree_node_compact()`, and `bch2_btree_build_aux_trees()`.

Dependencies and integration:
- Includes `btree/interior.h` for btree node/bset layout helpers.
- Used by read, write, split/interior update, and cache maintenance paths.

Risks and validation notes:
- `sort_iter_add()` asserts capacity but skips empty ranges, so callers must size the iterator for the maximum number of non-empty ranges they may add.
- Compaction thresholds directly influence node write frequency and insert latency.
