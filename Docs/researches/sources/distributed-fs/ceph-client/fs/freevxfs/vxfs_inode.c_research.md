# sources/distributed-fs/ceph-client/fs/freevxfs/vxfs_inode.c

## Purpose

`sources/distributed-fs/ceph-client/fs/freevxfs/vxfs_inode.c` translates VxFS on-disk inodes into Linux VFS inodes and provides inode lookup helpers for normal, structural, and extent-based metadata inodes. The complete 314-line file was read for this report.

## Important APIs, Types, and Functions

Important functions are `vxfs_blkiget()`, `vxfs_stiget()`, `vxfs_iget()`, and `vxfs_evict_inode()`, plus diagnostic `vxfs_dumpi()`. Internal helpers are `vxfs_transmod()`, `dip2vip_cpy()`, and `__vxfs_iget()`.

## Control Flow

`dip2vip_cpy()` endian-converts common disk inode fields into `vxfs_inode_info`, copies organization-specific data without conversion, and initializes VFS inode mode, uid/gid, link count, size, times, blocks, and generation. `vxfs_blkiget()` reads metadata inodes directly from a known extent via buffer cache during mount. `__vxfs_iget()` reads normal inodes from the inode-list mapping through pagecache. `vxfs_iget()` uses `iget_locked()`, fills new inodes, chooses address-space operations based on immediate vs mapped organization, and assigns regular, directory, symlink, or special inode operations.

## State and Persistence Behavior

The file populates in-core inode private state from persistent disk inodes. It does not write back VxFS metadata. Eviction truncates pagecache and clears VFS inode state.

## Dependencies and Integration Points

It integrates with mount setup (`vxfs_fshead.c`), directory lookup (`vxfs_lookup.c`), address-space operations (`vxfs_aops`, `vxfs_immed_aops`), generic read-only file ops, symlink inode operations, and old device decoding for special files.

## Risks and Edge Cases

Risks include trusting disk inode sizes, organization types, and device numbers; immediate symlink termination depends on inline buffer capacity; and metadata inodes loaded with `new_inode()` use generated inode numbers rather than disk numbers. Unsupported or malformed mode/type combinations can lead to wrong VFS operation assignment.

## Test Signals

Mount fixture images with regular files, directories, symlinks, immediate symlinks, device nodes, structural inodes, and corrupt inode-list blocks. KASAN and inode lifetime tracing are useful around failed `iget` and eviction paths.
