# File Research: sources/block-storage/thin-provisioning-tools/src/pdata/space_map/common.rs

Defines shared on-disk space-map structures. `IndexEntry` maps a bitmap index entry to bitmap block location plus free-count metadata. `Bitmap` packs 2-bit reference states for `Small(0)`, `Small(1)`, `Small(2)`, and `Overflow`, using the device-mapper bit ordering.

`SMRoot` stores total blocks, allocated blocks, bitmap root, and overflow ref-count root. `write_common` serializes normal space maps into bitmap blocks plus overflow btree. `write_metadata_common` handles metadata-space-map serialization using `WriteBatcher` allocations and writes zero-filled remaining bitmaps.
