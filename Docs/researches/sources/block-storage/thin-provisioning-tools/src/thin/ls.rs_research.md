# File Research: sources/block-storage/thin-provisioning-tools/src/thin/ls.rs

This file implements `thin_ls`, listing thin devices and optionally computing mapped, shared, exclusive, and highest-mapped usage fields.

Key elements:
- `OutputField` enumerates supported columns: device ID, mapped/exclusive/shared/highest in blocks, sectors, bytes, pretty units, and device timestamps/transaction.
- `FromStr` parses field names such as `DEV`, `MAPPED_BLOCKS`, `EXCLUSIVE`, and `SNAP_TIME`.
- `LsTable` formats rows with `GridLayout`, converting block counts to sectors/bytes using data block size and `SECTOR_SHIFT`.
- The btree traversal machinery mirrors `thin/check.rs` but uses `RestrictedTwoAggregator` and `HashVec` to track reference counts and summaries.
- `NodeSummary` includes `nr_shared` in addition to mapping counts and key ranges.
- `read_internal_nodes()`, `collect_nodes_in_use()`, `read_leaf_nodes()`, and `count_mapped_blocks()` discover and summarize mapping btrees.
- `examine_leaf_()` initially treats all leaf mappings as shared until exclusive leaves can be revisited.
- `read_exclusive_leaves()` identifies metadata leaves with reference count 1 and recomputes shared data block counts using data refcounts.
- `count_data_mappings()` loads device mapping roots, initializes restricted metadata/data aggregators, monitors progress, and returns summaries per root.
- `ls()` validates metadata consistency, reads device details, decides whether expensive counting is required, and renders output.

Interactions:
- Uses `is_superblock_consistent()` before listing.
- Uses `btree_to_map::<DeviceDetail>()` for device details.
- Uses `btree_to_value_vec()` to collect mapping roots.
- Shares many concepts with `thin/check.rs`, but computes reporting stats instead of repair decisions.

Risks and notes:
- Counting fields trigger a full mapping scan; metadata-only fields avoid that cost.
- Device details are zipped with mapping summaries; this relies on consistent btree ordering and prior superblock consistency.
- Hard-coded worker counts and batch sizes mirror the checker.
- If metadata contains errors during counting, the command fails rather than rendering partial usage.
