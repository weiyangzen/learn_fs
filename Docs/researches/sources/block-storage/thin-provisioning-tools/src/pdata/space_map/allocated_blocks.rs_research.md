# File Research: sources/block-storage/thin-provisioning-tools/src/pdata/space_map/allocated_blocks.rs

Builds a `RoaringBitmap` of allocated metadata blocks from a metadata space-map root. It loads the metadata index, sorts bitmap locations by physical block for read locality, reads each bitmap, and inserts any entry that is not `Small(0)`.

The returned roaring bitmap uses logical block numbers derived from index position times `ENTRIES_PER_BITMAP` plus bitmap entry offset.
