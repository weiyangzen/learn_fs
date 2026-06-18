# File Research: sources/block-storage/kvdo/vdo/vdo-layout.c

This file implements fixed partition layouts and the VDO-specific layout wrapper. `fixed_layout` tracks a free range and linked list of `partition` records; partitions have id, layout pointer, layer offset, partition-local base, count, and next pointer.

Fixed-layout operations:
- `vdo_make_fixed_layout()` creates an initially unpartitioned layout over `[start_offset, start_offset + total_blocks)`.
- `vdo_make_fixed_layout_partition()` carves a partition from the beginning or end, supports `VDO_ALL_FREE_BLOCKS`, rejects duplicate ids and insufficient space, updates free bounds, and prepends to the partition list.
- Translation helpers convert between partition-relative and layer PBNs with range checking.
- Accessors return total size, available blocks, partition size/offset/base, and partition lookup by id.

Encoding format:
- Layout format header is `VDO_FIXED_LAYOUT` version `3.0`.
- Encoded layout stores `first_free`, `last_free`, partition count, and each partition's id/offset/base/count in little-endian order.
- Decode validates the header minimum, ensures enough bytes for declared partitions, allocates a layout, and reconstructs partitions.

VDO layout behavior:
- `vdo_make_partitioned_fixed_layout()` creates standard partitions: block map from beginning, slab summary from end, recovery journal from end, and block allocator from remaining free space.
- `vdo_decode_layout()` validates all required partitions exist before returning `struct vdo_layout`.
- `prepare_to_vdo_grow_layout()` prepares a next layout for physical growth, creates a `dm_kcopyd` client if needed, preserves metadata partition sizes, and rejects too-small growth that would place new journal/summary over old metadata.
- `vdo_grow_layout()` swaps in the prepared layout, while `vdo_finish_layout_growth()` frees unused previous/next layouts.
- `vdo_copy_layout_partition()` uses `dm_kcopyd_copy()` to copy a partition from current to next layout, converting partitions to `dm_io_region`s with VDO geometry bio offset adjustment.

The file is the authoritative partitioning and growth coordinator for VDO metadata placement.
