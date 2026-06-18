# File Research: sources/block-storage/thin-provisioning-tools/src/thin/stat.rs

## Purpose
Provides statistics operations for thin metadata: data block reference-count histograms, metadata block reference-count histograms, and data mapping run-length histograms.

## Main Components
- `RefCounter` implements `NodeVisitor<u32>` for overflow ref-count btree values and accumulates a `BTreeMap<ref_count, count>` behind a `Mutex`.
- `gather_btree_index_entries()` loads bitmap index entries from a btree-backed space map.
- `gather_metadata_index_entries()` reads the metadata-space-map index block directly via `load_metadata_index()`.
- `stat_low_ref_counts_in_bitmap()` counts small bitmap refcounts in the range `1..=2`.
- `stat_low_ref_counts()` reads bitmap blocks, verifies each block is a bitmap via checksum type, unpacks `Bitmap`, and counts low inline refcounts.
- `stat_overflow_ref_counts()` walks the overflow ref-count tree and merges counts through `RefCounter`.
- `stat_data_block_ref_counts()` and `stat_metadata_block_ref_counts()` combine bitmap low counts and overflow tree counts.
- `RunLengthCounter` implements `NodeVisitor<BlockTime>` and uses `RunBuilder` to coalesce consecutive mapping runs.
- `stat_data_run_lengths()` walks each device mapping btree root from the top-level mapping tree.
- `ThinStatOpts`, `StatOp`, and `stat()` expose the command entry point.

## Behavior
Reference-count statistics are gathered from the two-level space-map representation. Low counts stored directly in bitmap entries are counted by scanning bitmap blocks. Larger or overflowed counts are counted by walking the ref-count btree. The data space map and metadata space map differ in how bitmap index entries are discovered, hence the separate gather helpers.

Run-length statistics read the top-level mapping btree to find per-thin-device mapping roots, then walk each mapping btree. `RunBuilder` receives ordered `(thin block, data block, time)` tuples and emits a completed run when continuity breaks. `end_walk()` flushes the final pending run.

Output is printed as tabular stdout:
- ref-count operations print `ref-count`, `times`, percentage, total allocated blocks, and average ref count;
- run-length operation prints `length`, `counts`, percentage, total runs/leaves, and average run length.

## Dependencies and Interactions
The file depends on btree traversal, btree-to-map conversion, metadata block checksums, space-map unpacking, thin block-time values, the superblock reader, and command engine construction.

## Research Notes
The visitor structs use `Mutex` and `AtomicU64` because `BTreeWalker` visitor APIs are shareable/concurrency-friendly, even though the visible call sites walk synchronously. Error messages intentionally collapse lower-level walk errors for user-facing stat commands.
