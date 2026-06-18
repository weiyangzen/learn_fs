# sources/distributed-fs/ceph-client/fs/udf/balloc.c

## Purpose

`sources/distributed-fs/ceph-client/fs/udf/balloc.c` implements UDF block allocation and free-space accounting for partitions backed either by an unallocated-space bitmap or an unallocated-space table. The source was read as a complete 735-line implementation.

## Important APIs, Types, and Functions

Public entry points are `udf_free_blocks`, `udf_prealloc_blocks`, and `udf_new_block`. Bitmap helpers include `read_block_bitmap`, `load_block_bitmap`, `udf_bitmap_free_blocks`, `udf_bitmap_prealloc_blocks`, and `udf_bitmap_new_block`. Table helpers include `udf_table_free_blocks`, `udf_table_prealloc_blocks`, and `udf_table_new_block`. `udf_add_free_space` updates the logical volume integrity descriptor free-space table. Local bit helpers wrap little-endian bitmap operations.

## Control Flow

For bitmap-backed partitions, allocation loads the relevant bitmap block, searches near the goal for a set free bit, optionally scans other bitmap groups, clears the bit, marks the bitmap dirty, updates free-space accounting, and returns the logical block. Preallocation clears consecutive free bits from a requested start until a used bit or partition end. Freeing sets bits back to one, handling bitmap group boundaries.

For table-backed partitions, allocation scans unallocated extents for the closest block to the goal, allocates only from an extent start, then rewrites or deletes that extent. Preallocation finds an extent beginning at `first_block` and shrinks or deletes it. Freeing tries to merge with adjacent free extents and, if necessary, adds a new extent, including the special path that steals a block from the freed range to create an indirect allocation extent without recursively allocating while holding `s_alloc_mutex`.

## State and Persistence Behavior

All allocation changes are serialized by `UDF_SB(sb)->s_alloc_mutex`. Bitmap changes dirty space bitmap buffers; table changes rewrite allocation descriptors of the unallocated-space table inode. Free-space counters are updated in `logicalVolIntegrityDesc.freeSpaceTable` when an LVID buffer is present, and `udf_updated_lvid` records the change. Inode block counts are adjusted when allocation/freeing is associated with an inode.

## Dependencies and Integration Points

The file depends on UDF superblock and inode private structures, Linux bit operations, overflow checking, buffer-head I/O, and extent helpers from `inode.c` (`udf_next_aext`, `udf_write_aext`, `udf_add_aext`, `udf_delete_aext`, `udf_setup_indirect_aext`). It is used by inode allocation, data block mapping, truncation, preallocation discard, and directory append paths.

## Risks and Edge Cases

Bitmap verification rejects reserved bits that are unexpectedly marked free, caching `ERR_PTR(-EFSCORRUPTED)` to avoid retrying known-bad bitmap groups. Public free validates overflow and partition length, but table operations still have complex extent overflow limits near `0x3fffffff`. Error handling under `s_alloc_mutex` must not leak buffer heads or leave counters inconsistent. `udf_bitmap_new_block` reports many load errors as `-EIO`, including corruption paths. Preallocation/free-space updates pass negative counts through an unsigned-looking helper parameter, relying on two's complement conversion into `le32_add_cpu`.

## Test Signals

Tests should cover bitmap and table partitions, allocation near a goal, wraparound allocation, preallocation, freeing across bitmap group boundaries, table extent merging/splitting, ENOSPC, corrupted bitmap reserved bits, partition-boundary overflow checks, LVID free-space counter updates, and block accounting on inodes.
