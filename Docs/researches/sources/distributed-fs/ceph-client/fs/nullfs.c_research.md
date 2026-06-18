# sources/distributed-fs/ceph-client/fs/nullfs.c

## Purpose
`nullfs.c` defines a permanently empty, immutable, kernel-internal filesystem named `nullfs`. It provides a single global superblock instance with an empty root directory and no user mount surface.

## Important APIs and Functions
`nullfs_super_operations` supplies `simple_statfs`. `nullfs_fs_fill_super()` initializes superblock geometry, magic, operation tables, xattr/export settings, timestamp granularity, and root inode. `nullfs_fs_get_tree()` returns a singleton tree. `nullfs_init_fs_context()` marks the context global, no-user, noexec, and nodev. `nullfs_fs_type` exports the filesystem type with `kill_anon_super`.

## Control Flow
The VFS calls `init_fs_context`, then `get_tree_single()` calls the fill routine on first creation. The fill path allocates one inode, turns it into an empty directory, initializes timestamps, assigns inode number 1, marks it immutable, and installs it as root.

## State and Persistence Behavior
There is no backing store and no persistent metadata. The only state is the singleton anonymous superblock and immutable empty root inode. There are no xattrs, export operations, write paths, children, or block-device interactions.

## Dependencies and Integration Points
It depends on Linux fs_context, superblock, simple directory inode, and magic helpers. Other kernel code can reference `nullfs_fs_type` as an internal empty filesystem.

## Risks
The main risk is accidental expansion of a deliberately empty singleton into a user-mountable or writable filesystem without lifecycle and isolation design.

## Test Signals
Verify singleton behavior, root inode number 1, directory mode, immutable flag, empty readdir, no xattrs, `simple_statfs`, no user mounts, and teardown through `kill_anon_super`.
