<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/efs/efs.h -->
# sources/distributed-fs/ceph-client/fs/efs/efs.h

## Purpose
`efs.h` centralizes EFS in-memory and on-disk format definitions, constants, macros, and cross-file prototypes.

## Important APIs, types, and functions
It defines block size constants, `efs_block_t`, `efs_ino_t`, `efs_extent`, `struct efs_dinode`, `struct efs_inode_info`, directory entry/block structures, and helper macros such as `INODE_INFO`, `SUPER_INFO`, `EFS_SLOTAT`, and magic checks. It declares inode, lookup, block mapping, export, and symlink operation objects used across EFS files.

## Control flow
The header has no runtime flow, but its extent and directory layout definitions drive all block mapping, inode loading, directory iteration, and lookup behavior.

## State and persistence
It describes persistent on-disk state: 512-byte blocks, 128-byte dinodes, direct/indirect extents, EFS directory blocks, superblock information, and SGI device encodings. Runtime state extends VFS inodes with cached extents and last-extent index.

## Dependencies and integration points
It depends on Linux VFS/uaccess types and `linux/efs_fs_sb.h`. It is included by every EFS implementation file and forms the local ABI of the driver.

## Risks and test signals
Risks include bitfield/endian assumptions in `efs_extent`, structure layout drift, incorrect slot arithmetic, and stale prototypes. Test signals include big-endian/little-endian image parsing, direct and indirect extents, special device inodes, and compile-time warnings under different architectures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/efs/efs.h -->
