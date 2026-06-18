# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_metadir.c

Purpose: Implements the metadata directory tree abstraction for metadata inodes stored in a hidden internal namespace. It provides lookup, create, link in userspace builds, commit/cancel, and mkdir helpers.

Important APIs: `xfs_metadir_load`, `xfs_metadir_start_create`, `xfs_metadir_create`, userspace-only `xfs_metadir_start_link` and `xfs_metadir_link`, `xfs_metadir_commit`, `xfs_metadir_cancel`, and `xfs_metadir_mkdir`. Private helpers set `xfs_name`, perform directory lookup with type validation, and tear down update state.

Control flow: load converts a path component to `xfs_name`, locks the parent directory, looks up the inode, validates inode number/type, then calls `xfs_trans_metafile_iget`. Create starts by allocating parent-pointer context and a create transaction, then locks the parent. `xfs_metadir_create` verifies nonexistence, allocates an inode, initializes it, marks it as a metadata file, joins the parent after possible transaction rolling, and creates the directory entry with parent pointer arguments. Commit commits the transaction and releases locks/context; cancel aborts and releases. `xfs_metadir_mkdir` wraps start/create/commit and handles partially created inode cleanup.

State and persistence: mutates the metadata directory tree, creates metadata inode cores, directory entries, parent pointer attrs, and inode flags. Update state tracks held locks, transaction, parent args, and created inode.

Dependencies and integration: depends on directory code, inode allocation/init, transaction reservations, parent pointers, metadata inode flags, health marking, and shutdown checks. It deliberately excludes legacy quota/realtime bitmap/summary inode management from this abstraction.

Risks and test signals: risks include lock/transaction cleanup on partial create, exposing metadata inodes without required flags, directory type mismatches, and parent-pointer consistency. Tests should cover missing/existing path components, shutdown behavior, metadir mkdir failure injection, quota exclusion, parent-pointer enabled/disabled filesystems, and repair of sick metadir state.
