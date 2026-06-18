<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/efs/inode.c -->
# sources/distributed-fs/ceph-client/fs/efs/inode.c

## Purpose
`inode.c` loads EFS inodes from disk, assigns VFS operations, implements extent-based block mapping, and provides address-space operations for file and symlink data.

## Important APIs, types, and functions
Important functions include `efs_iget`, `extent_copy`, `efs_map_block`, `efs_extent_check`, `efs_read_folio`, and `_efs_bmap`. The file defines `efs_aops`, uses `struct efs_inode_info`, and exports module metadata.

## Control flow
`efs_iget` computes the disk block and offset of a 128-byte dinode from the inode number, cylinder group layout, and filesystem start offset. It reads the dinode, decodes mode, links, uid/gid, size, timestamps, device numbers, extent count, and direct extents, then assigns directory, regular file, symlink, or special inode operations. `efs_map_block` first checks the cached last extent and direct extents; for files with more than `EFS_DIRECTEXTENTS`, it walks indirect extent blocks referenced by the direct extents and maps logical blocks to physical blocks.

## State and persistence
Persistent state is the read-only EFS dinode and extent tree. Runtime state caches direct extents and the last successful extent index in `struct efs_inode_info` to speed repeated mappings.

## Dependencies and integration points
It depends on buffer-head block reads, VFS inode cache, generic block mapping/read helpers, EFS superblock layout from `efs_sb_info`, and symlink operations from `symlink.c`.

## Risks and test signals
Risks include inode-number arithmetic errors, indirect extent traversal bugs, extent magic validation, corrupted device encodings, unsupported modes, and stale `lastextent` assumptions. Test signals include regular reads over fragmented direct and indirect extents, symlink reads, special device nodes, zero-size files, bad extent magic images, and NFS/export inode retrieval.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/efs/inode.c -->
