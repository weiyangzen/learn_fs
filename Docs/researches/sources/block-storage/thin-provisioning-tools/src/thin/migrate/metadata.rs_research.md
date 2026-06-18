# File Research: sources/block-storage/thin-provisioning-tools/src/thin/migrate/metadata.rs

This file reads thin metadata needed for migration streams.

Key elements:
- `ArcEngine` aliases shared `IoEngine`.
- `read_by_thin_id()` performs a btree lookup by thin ID and returns a cloned unpacked value, or errors if missing.
- `read_device_detail()` reads a `DeviceDetail` from the details tree.
- `read_mapping_root()` reads the per-thin mapping tree root from the top-level mapping tree.
- `ThinIterator` stores thin ID, data block size, a `BTreeIterator<BlockTime>`, and mapped block count.
- `ThinIterator::new()` reads the metadata snapshot superblock, finds the device detail and mapping root for the thin ID, and constructs a mapping iterator.

Interactions:
- Used by `ThinStream` in `stream.rs`.
- Uses `read_superblock_snap()`, so migration reads a metadata snapshot rather than live mutable roots.

Risks and notes:
- Missing metadata snapshot or missing thin ID fails stream construction.
- The iterator depends on mapping btree ordering.
