<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/efs/symlink.c -->
# sources/distributed-fs/ceph-client/fs/efs/symlink.c

## Purpose
`symlink.c` supplies EFS symlink address-space behavior so symbolic link targets can be read from read-only EFS extents.

## Important APIs, types, and functions
The exported object is `efs_symlink_aops`. The main callback reads symlink data through the same block-mapping mechanism used for regular file data.

## Control flow
When a symlink inode is loaded, `efs_iget` assigns `page_symlink_inode_operations`, disables highmem for the inode, and attaches `efs_symlink_aops`. Link resolution then reads folios through block mapping, ultimately using `efs_get_block`/`efs_map_block`.

## State and persistence
No state changes occur. Persistent symlink contents live in the EFS extent-backed file data.

## Dependencies and integration points
It integrates with VFS page symlink operations, EFS inode setup, and the extent mapping code in `inode.c`.

## Risks and test signals
Risks include truncated symlink targets, block mapping failures, and highmem assumptions. Test signals include short and multi-block symlinks, broken/corrupt extent maps, and path resolution through nested symlinks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/efs/symlink.c -->
