# File Research: sources/block-storage/thin-provisioning-tools/src/thin/device_detail.rs

This file defines the on-disk value type for the thin device details btree.

Key elements:
- `DeviceDetail` fields:
  - `mapped_blocks: u64`
  - `transaction_id: u64`
  - `creation_time: u32`
  - `snapshotted_time: u32`
- `Display` prints all four fields in a compact diagnostic form.
- `Unpack::disk_size()` returns 24 bytes.
- `unpack()` reads the fields little-endian.
- `Pack::pack()` writes the fields little-endian.

Interactions:
- Used by check, ls, dump, restore, repair, migration metadata, and metadata repair root inference.
- Stored in the device details btree keyed by thin device ID.

Risks and notes:
- It is a simple POD-style disk structure; validation of semantic consistency is done by callers.
