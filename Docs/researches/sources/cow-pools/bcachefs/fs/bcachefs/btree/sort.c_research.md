# File Research: sources/cow-pools/bcachefs/fs/bcachefs/btree/sort.c

This file implements B-tree key sorting, repacking, whiteout handling, and node compaction.

Key behavior:
- `sort_iter` merges multiple already-sorted bset ranges.
- `bch2_key_sort_fix_overlapping()` builds a clean set from read bsets, dropping deleted keys and older duplicate-position keys.
- `bch2_sort_repack()` rewrites keys into a new key format, optionally filtering whiteouts.
- `bch2_sort_keys_keep_unwritten_whiteouts()` is used by writeback to preserve only whiteouts that still matter for unwritten data.
- `bch2_sort_keys()` compacts in-memory nodes and drops deleted keys.
- Bounce-buffer helpers allocate from `kvmalloc()` first and fall back to a mempool.
- `bch2_sort_whiteouts()`, `bch2_drop_whiteouts()`, and `bch2_compact_whiteouts()` clean whiteout storage.
- `bch2_btree_node_sort()` merges a range of bsets and updates `btree_nr_keys`, bset offsets, and aux-tree state.
- `bch2_btree_node_compact()` decides which written/unwritten bsets to merge when a node is near the `MAX_BSETS` limit.
- `bch2_btree_build_aux_trees()` rebuilds search trees for each bset.

Important invariants:
- Bsets are individually sorted; merge iterators exploit this.
- Whiteouts are treated differently for read normalization, in-memory compaction, and writeback.
- After compaction, key accounting and auxiliary trees must be rebuilt.
