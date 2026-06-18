# sources/distributed-fs/ceph-client/fs/freevxfs/vxfs.h

## Purpose

`sources/distributed-fs/ceph-client/fs/freevxfs/vxfs.h` defines the FreeVxFS superblock ABI, byte-order helpers, VxFS mode/type constants, inode organization constants, and in-core superblock private state. The complete 257-line file was read for this report.

## Important APIs, Types, and Functions

Important definitions include `VXFS_SUPER_MAGIC`, `VXFS_ROOT_INO`, `struct vxfs_sb`, `struct vxfs_sb_info`, `enum vxfs_byte_order`, `__fs16/__fs32/__fs64`, `fs16_to_cpu()`, `fs32_to_cpu()`, `fs64_to_cpu()`, `enum vxfs_mode`, `VXFS_TYPE_MASK`, `VXFS_IS*` type predicates, `VXFS_ORG_*`, organization predicates, and `VXFS_SBI()`.

## Control Flow

The header has no independent runtime flow. Runtime users set `vxfs_sb_info.byte_order` during superblock probing, then all on-disk integer reads pass through the endian helpers. Type and organization macros steer inode setup, block mapping, immediate-data handling, and metadata discovery.

## State and Persistence Behavior

`struct vxfs_sb` mirrors on-disk superblock fields, including version, block geometry, free counts, OLT location, inode sizing, and legacy version fields. `struct vxfs_sb_info` stores the mounted instance's raw superblock buffer, structural inodes, OLT extent, fileset header inode, initial inode-list extent, and byte order.

## Dependencies and Integration Points

This header is shared by every FreeVxFS implementation file. It depends on Linux integer types and endian conversion helpers and integrates with VFS `super_block->s_fs_info` through `VXFS_SBI()`.

## Risks and Edge Cases

The struct layout is an on-disk ABI; incorrect field offsets or endian conversion mistakes can corrupt all higher-level interpretation. The driver only models a subset of full VxFS superblock fields, so unsupported versions or ports may contain valid metadata beyond the modeled structure.

## Test Signals

Signals include mounting little-endian UnixWare and big-endian HP-UX images, validating statfs values, sparse/smatch checks for `__bitwise` endian misuse, and regression images for VxFS versions 2 through 4.
