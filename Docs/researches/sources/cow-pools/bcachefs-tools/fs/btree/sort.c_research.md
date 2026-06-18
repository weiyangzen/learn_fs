# File Research: sources/cow-pools/bcachefs-tools/fs/btree/sort.c

Read completeness: full file read, 609 lines.

Purpose: sorting, repacking, duplicate/whiteout filtering, compaction, and aux-tree rebuild logic for btree node bsets. It is used after reads, before writes, during node compaction, and when copying keys between nodes.

Major components:
- `sort_iter_*()` implements a small multi-run merge iterator over sorted bsets. It keeps the smallest current key at `data[0]` by local sifting instead of a heap.
- `bch2_key_sort_fix_overlapping()` sorts read bsets, drops deleted keys and older same-position keys, and returns live key accounting.
- `bch2_sort_repack()` walks a `btree_node_iter`, optionally drops whiteouts, transforms keys into a new bkey format, and accounts packed/unpacked keys.
- `bch2_sort_keys_keep_unwritten_whiteouts()` sorts write-output keys while preserving unwritten whiteouts that still matter and dropping overwritten whiteouts.
- `bch2_sort_keys()` is the normal in-memory compaction sorter that drops all deleted keys.
- Bounce allocation helpers allocate temporary node-sized buffers from fast kvmalloc or the btree bounce mempool.
- Whiteout helpers include `bch2_set_bset_needs_whiteout()`, `bch2_sort_whiteouts()`, `bch2_drop_whiteouts()`, and `bch2_compact_whiteouts()`.
- Node compaction and copying helpers include `bch2_btree_node_sort()`, `bch2_btree_sort_into()`, `bch2_btree_node_compact()`, and `bch2_btree_build_aux_trees()`.

Control-flow and invariants:
- Read-time sorting uses pointer order as a tie breaker so newer/older bsets can be resolved deterministically by later logic.
- Write-time sorting explicitly adds the unwritten whiteout range into the sort iterator before outputting a disk bset.
- `bch2_btree_node_sort()` can sort the entire node into a bounce buffer and swap node buffers to avoid a full copy when memory profiling is disabled.
- `bch2_drop_whiteouts()` may also move unwritten bset entries down in memory so the write block area remains contiguous.
- After compaction/sort, the code rebuilds aux trees and verifies key accounting with `bch2_verify_btree_nr_keys()`.

Dependencies and integration:
- Depends on packed key comparison, bset helpers, btree interior layout, extents, scheduler/memalloc flags, and node-size options.
- Read path uses `bch2_key_sort_fix_overlapping()`.
- Write path uses `bch2_sort_whiteouts()` and `bch2_sort_keys_keep_unwritten_whiteouts()`.
- Update/insert paths rely on compaction helpers to maintain `MAX_BSETS` constraints.

Risks and validation notes:
- Some unpack helpers read before key memory for optimized field extraction; `bch2_sort_whiteouts()` pads its bounce allocation to keep that valid.
- Whiteout compaction relies on `needs_whiteout` semantics; dropping the wrong deleted key can alter snapshot/extent overwrite semantics.
- `should_compact_all()` encodes a geometric-size heuristic between full node size and write-set buffer size; tuning affects write amplification and insert cost.
