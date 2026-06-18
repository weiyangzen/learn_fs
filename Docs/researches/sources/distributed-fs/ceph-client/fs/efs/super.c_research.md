<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/efs/super.c -->
# sources/distributed-fs/ceph-client/fs/efs/super.c

## Purpose
`super.c` registers EFS, parses SGI volume headers and EFS superblocks, forces read-only mounts, owns the EFS inode slab, and reports filesystem statistics.

## Important APIs, types, and functions
Important functions include `init_efs_fs`, `exit_efs_fs`, `efs_init_fs_context`, `efs_get_tree`, `efs_fill_super`, `efs_validate_vh`, `efs_validate_super`, `efs_statfs`, `efs_kill_sb`, and inode-cache helpers. It defines `efs_fs_type`, `efs_superblock_operations`, and `efs_export_ops`.

## Control flow
Module init creates the inode cache and registers the filesystem. Mount allocates `efs_sb_info`, sets 512-byte block size, reads block 0 as an SGI volume header, validates checksum and chooses an EFS partition start if present, reads the EFS superblock, decodes geometry and counters, forces `SB_RDONLY`, installs super/export operations, loads the root inode, and creates the root dentry. Reconfigure syncs and preserves read-only state. Kill-super frees block-super resources and `s_fs_info`.

## State and persistence
Runtime superblock state includes filesystem start, total blocks/groups, inode blocks, and free counters decoded from disk. EFS is read-only, so persistent disk state is not modified.

## Dependencies and integration points
It depends on block devices, buffer heads, fs_context, SGI volume header definitions, EFS superblock definitions, VFS exportfs, and the EFS inode loader.

## Risks and test signals
Risks include memory leaks on early mount errors, SGI partition-table checksum handling, accepting invalid geometry, root inode failures, and read-only enforcement. Test signals include mounting whole disks with SGI labels, mounting partitions without labels, invalid magic/checksum images, remount rw attempts, statfs values, and module load/unload loops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/efs/super.c -->
