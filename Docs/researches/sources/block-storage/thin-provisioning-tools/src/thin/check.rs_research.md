# File Research: sources/block-storage/thin-provisioning-tools/src/thin/check.rs

This is the main thin metadata consistency checker. It verifies superblock roots, device/details consistency, mapping btrees, mapped-block counts, data space map counts, metadata space map counts, and optionally repairs leak-only space map discrepancies.

Key elements:
- `ThinCheckOptions` carries input path, engine options, `sb_only`, `skip_mappings`, `ignore_non_fatal`, `auto_repair`, `clear_needs_check`, root overrides, and report.
- `inc_superblock()` accounts for the primary superblock and metadata snapshot in the metadata reference aggregator.
- `NodeMap` records discovered btree nodes using packed type bits: none, leaf, internal, or error. It tracks internal child metadata, leaf nodes, and node-local errors.
- `LayerHandler` implements `ReadHandler` for internal btree layers. It verifies checksums, unpacks internal nodes, records children, increments metadata reference counts, and batches node-map updates.
- `read_internal_nodes()` walks mapping trees breadth/layer-wise to reduce seek-heavy depth-first behavior.
- `examine_leaf_()` validates mapping-tree leaves: checksum, header fields, value size, max entries, block number, entry count, key order, padding, and data-block bounds.
- `LeafHandler` reads leaves in batches, increments the data reference aggregator for valid mappings, and stores `NodeSummary`.
- `summarize_tree()` and `count_mapped_blocks()` verify parent key ranges, underfull nodes, ordering, overlap, and aggregate mapping counts per tree.
- `check_mapped_blocks()` compares computed mapping counts against `DeviceDetail.mapped_blocks`.
- `get_thins_from_superblock()` loads and cross-checks top-level mapping roots and device details.
- `get_thins_from_metadata_snap()` handles metadata snapshots, including devices exclusive to the snapshot.
- `compare_space_maps()` diffs reconstructed aggregators against on-disk space maps, distinguishing leaks from bad reference counts.
- `check()` orchestrates the full command, including optional `clear_needs_check_flag()` and leak repair via `repair_space_map()`.
- `check_with_maps()` exposes validated metadata/data aggregators for callers that need allocated-block maps.

Interactions:
- Depends heavily on pdata btree, btree utilities, space map aggregators/loaders/repairers, superblock parsing, `DeviceDetail`, `BlockTime`, and `Report`.
- Uses background futures to read on-disk data and metadata space maps while mapping traversal runs.
- Uses `ProgressMonitor` for combined metadata/data scanning progress.

Risks and notes:
- Fixed worker counts (`NR_THREADS = 4`, `NR_UNPACKERS = 4`) are hard-coded.
- Several thread closures ignore errors during internal-node collection, deferring detection to later node summaries.
- Non-fatal checking mode changes structural validation, especially underfull and max-entry divisibility checks.
- Auto-repair only handles leak-style discrepancies; bad reference counts remain fatal.
- The metadata snapshot path intentionally avoids comparing on-disk space maps.
