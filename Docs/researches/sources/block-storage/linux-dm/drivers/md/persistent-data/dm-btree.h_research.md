# File Research: sources/block-storage/linux-dm/drivers/md/persistent-data/dm-btree.h

## Purpose
Public interface for persistent hierarchical B+ trees.

## Main Definitions
- Sparse annotation macros:
  - `__dm_written_to_disk`
  - `__dm_reads_from_disk`
  - `__dm_bless_for_disk`
  - `__dm_unbless_for_disk`
- `struct dm_btree_value_type`: value size plus optional `inc`, `dec`, and `equal` callbacks for reference-counted values.
- `struct dm_btree_info`: transaction-manager binding, number of nested tree levels, and leaf value type.
- `struct dm_btree_cursor`: cursor state with fixed maximum depth.

## API Contract
- Btrees store 64-bit keys and fixed-size values.
- Multi-level support means nested btrees, not the depth of one tree.
- Deletion of an entire tree is O(n) and may block; callers should keep it off I/O paths.
- Insert and remove operations return new roots.
- Value callbacks are responsible for reference-count side effects of copied, overwritten, and deleted values.
- Walk is single-level only, while lookup/insert/remove can use multiple `keys[]` levels.

## Exposed Functions
Create/delete, lookup/lookup-next, insert/insert-notify, remove/remove-leaves, lowest/highest key discovery, walk, and cursor operations.
