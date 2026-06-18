<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/super.c -->
# sources/distributed-fs/ceph-client/fs/jfs/super.c

## Purpose
`super.c` is the JFS filesystem registration, mount, remount, superblock, quota, freeze, sync, and module lifecycle implementation. It converts fs_context parameters into `jfs_sb_info`, mounts block devices, starts/stops JFS service threads, and wires JFS into VFS superblock/export/quota operations.

## Important APIs, types, and functions
Key functions are `jfs_error`, `jfs_alloc_inode`, `jfs_free_inode`, `jfs_statfs`, `jfs_put_super`, `jfs_parse_param`, `jfs_reconfigure`, `jfs_fill_super`, `jfs_freeze`, `jfs_unfreeze`, `jfs_get_tree`, `jfs_sync_fs`, `jfs_show_options`, quota helpers, `jfs_init_fs_context`, `init_jfs_fs`, and `exit_jfs_fs`. Important state includes `jfs_inode_cachep`, `commit_threads`, `jfsCommitThread[]`, `jfsIOthread`, `jfsSyncThread`, `struct jfs_context`, `jfs_super_operations`, `jfs_export_operations`, and `jfs_fs_type`.

## Control flow
Mount option parsing handles integrity, charset, resize, error policy, quota flags, uid/gid/umask, and discard thresholds. `jfs_fill_super` allocates `jfs_sb_info`, transfers parsed options, validates discard support, creates the direct-mapping metadata inode, runs `jfs_mount`, optionally runs `jfs_mount_rw`, installs xattr/quota/export operations, loads the root inode, and sets max file size/time granularity. Reconfigure syncs the filesystem, updates options, optionally calls `jfs_extendfs`, transitions read-only to read-write or back through quota suspend/resume and mount/unmount-rw helpers, and remounts when the integrity mode changes. Freeze quiesces transactions, shuts down the log, and marks the superblock clean; unfreeze marks mounted, reinitializes the log, and resumes transactions.

Module initialization creates the JFS inode slab, initializes metapages and transaction manager, starts IO, lazy commit, and sync kthreads, initializes proc entries when configured, and registers the filesystem. Exit reverses these resources and waits for RCU inode frees before destroying the slab.

## State and persistence behavior
Persistent state managed here includes superblock clean/dirty/mounted flags, journal flush state, quota file data, and mount option effects persisted via inode flags for quota files. Runtime state includes `jfs_sb_info`, NLS tables, direct inode page cache, thread lifetimes, inode cache objects, fs_context private data, and error-policy bits controlling continue/remount-ro/panic behavior.

## Dependencies and integration points
It depends on VFS fs_context, block-device mounting, quota core, exportfs, xattr handlers, buffer_head/direct metadata mapping, JFS mount/log/metapage/transaction subsystems, POSIX ACL configuration, NLS, kthreads, procfs statistics, and the resize implementation.

## Risks and test signals
Risks include option lifetime for NLS tables, remount error paths that alter flags in the wrong order, read-only/read-write quota transitions, freeze failure leaving transactions blocked, service-thread startup cleanup, direct inode cache invalidation after fsck, and quota I/O bypassing page cache. Tests should cover all mount/remount options, resize-on-remount only, rw/ro transitions with quotas, discard unsupported devices, freeze/unfreeze under load, mount failure unwinding, statfs estimates, NFS export handles, and module init failure injection at each thread/subsystem boundary.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/super.c -->
