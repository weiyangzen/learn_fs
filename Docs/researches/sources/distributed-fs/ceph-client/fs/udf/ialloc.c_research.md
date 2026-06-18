# sources/distributed-fs/ceph-client/fs/udf/ialloc.c

## Purpose

`sources/distributed-fs/ceph-client/fs/udf/ialloc.c` implements UDF inode allocation and freeing. It allocates one disk block for a new file entry and initializes the VFS and UDF-private inode fields. The source was read as a complete 113-line implementation.

## Important APIs, Types, and Functions

The public functions are `udf_free_inode` and `udf_new_inode`.

## Control Flow

`udf_new_inode` allocates a VFS inode, allocates private `i_data` sized for either `extendedFileEntry` or `fileEntry`, allocates a new block near the parent directory's ICB location, assigns a unique ID from the logical volume integrity descriptor, initializes ownership with mount UID/GID overrides, fills the UDF logical block address and VFS inode number, initializes allocation lengths/checkpoint/extra permissions, chooses in-ICB/short-ad/long-ad allocation mode from mount flags, initializes timestamps, inserts the inode locked into the inode hash, and marks it dirty. `udf_free_inode` frees the file-entry block through `udf_free_blocks`.

## State and Persistence Behavior

New inode state includes `i_location`, `i_unique`, `i_generation`, ownership, `i_lenEAttr`, `i_lenAlloc`, `i_use`, `i_checkpoint`, `i_extraPerms`, allocation descriptor type, timestamps, and dirty state. The persistent file entry is not written immediately here; marking dirty causes `inode.c` to serialize it later. Freeing returns the file-entry block to the partition free-space structures.

## Dependencies and Integration Points

The file depends on `new_inode`, inode ownership helpers, UDF mount flags, logical volume unique ID allocation, block allocation/freeing in `balloc.c`, private inode/superblock state, `insert_inode_locked`, and `udf_update_extra_perms` from `inode.c`. It is used by name creation paths.

## Risks and Edge Cases

Allocation failures after `new_inode` must mark and drop a bad inode. If `insert_inode_locked` fails, the already allocated disk block is not explicitly freed in this function, so the eviction path must be considered for leak behavior. Mount flags control FE/EFE and allocation descriptor mode, and changing them affects on-disk compatibility. `i_data` size must match the selected FE/EFE layout and block size.

## Test Signals

Tests should create files/directories/symlinks under FE and EFE modes, in-ICB/short-ad/long-ad modes, UID/GID override modes, and ENOSPC fault injection during block allocation and inode hash insertion. Free-space accounting should be checked after create/unlink cycles.
