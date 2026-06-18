# sources/distributed-fs/ceph-client/fs/jfs/file.c

## Purpose
Defines regular-file JFS VFS operations: fsync, open/release, setattr/truncate, fileattr/ioctl wiring, listxattr, ACL hooks, and generic I/O operation tables.

## Important APIs, types, and functions
`jfs_fsync()`, `jfs_open()`, `jfs_release()`, `jfs_setattr()`, `jfs_file_inode_operations`, and `jfs_file_operations`.

## Control flow
`fsync` writes the requested range then commits dirty inode metadata or flushes the journal. `open` validates file size, initializes quotas, and marks an active allocation group for new writable files. `release` decrements the active AG counter. `setattr` validates, handles quota transfer, waits for DIO on size changes, truncates, copies attributes, marks dirty, and updates ACLs on mode changes.

## State and persistence behavior
Persistent effects include inode metadata, journal commits, quota updates, and extent truncation. Runtime-only state includes `active_ag` and `bmap->db_active[]`.

## Dependencies and integration points
Integrates with VFS operations, quota APIs, page cache writeback, JFS transaction/inode/truncate code, xattr, ACL, ioctl, and dmap AG accounting.

## Risks and test signals
Test fsync/datasync durability, AG counter cleanup, DIO/truncate races, quota ownership changes, fileattr ioctls, and ACL chmod integration.
