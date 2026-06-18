# sources/distributed-fs/ceph-client/fs/freevxfs/vxfs_bmap.c

## Purpose

`sources/distributed-fs/ceph-client/fs/freevxfs/vxfs_bmap.c` maps FreeVxFS logical file blocks to physical disk blocks for internal reads and generic block mapping. It handles ext4-style VxFS extents and typed extents. The complete 271-line file was read for this report.

## Important APIs, Types, and Functions

The exported internal API is `vxfs_bmap1(struct inode *, long)`. Internal helpers are `vxfs_bmap_ext4()`, `vxfs_bmap_indir()`, `vxfs_bmap_typed()`, and diagnostic `vxfs_typdump()`. It consumes `struct vxfs_inode_info`, `struct vxfs_ext4`, `struct vxfs_typed`, `struct vxfs_typed_dev4`, and organization/type constants from `vxfs_inode.h`.

## Control Flow

`vxfs_bmap1()` dispatches by inode organization. Ext4-style mapping walks direct extents first, then reads an indirect block and indexes it for remaining logical blocks. Typed mapping scans the inode's inline typed extents; data extents return block plus offset, indirect extents recurse into extent blocks, and DEV4 extents are reported but unsupported. Unknown extent types trigger `BUG()`.

## State and Persistence Behavior

The code reads mapping state from on-disk inode extent descriptors and indirect extent blocks; it does not mutate metadata. Buffer heads are acquired with `sb_bread()` and released with `brelse()`.

## Dependencies and Integration Points

`vxfs_subr.c` calls `vxfs_bmap1()` from `vxfs_bread()`, `vxfs_getblk()`, and `generic_block_bmap()` paths. Inode setup in `vxfs_inode.c` assigns address-space operations that eventually invoke this mapper for regular files, symlinks, directories, and metadata inodes.

## Risks and Edge Cases

Malformed extent sizes, indirect block addresses, unsupported DEV4 extents, and unknown type values can produce failed reads or kernel warnings. The ext4 indirect indexing expression is subtle and historically fragile; boundary tests are important. Recursion in typed indirect extents can consume stack on adversarial images.

## Test Signals

Use fixture images with direct extents, indirect extents, typed data extents, holes/unmapped blocks, immediate files, and unsupported DEV4 descriptors. Fuzzed VxFS images plus KASAN/UBSAN can exercise malformed extent records.
