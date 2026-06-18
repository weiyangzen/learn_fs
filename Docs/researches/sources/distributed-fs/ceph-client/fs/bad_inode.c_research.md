# sources/distributed-fs/ceph-client/fs/bad_inode.c

Purpose: supplies the VFS sentinel operations used when an inode cannot be read or must be invalidated as permanently unusable.

Important APIs/types/functions: `make_bad_inode`, `is_bad_inode`, `iget_failed`, `bad_inode_ops`, and `bad_file_ops`. Most inode and file callbacks return `-EIO`; symlink and ACL callbacks return error pointers.

Control flow: a filesystem that fails during inode construction calls `iget_failed()`, which converts the inode to bad operations, unlocks it, and drops it. `make_bad_inode()` removes it from the inode hash, sets a regular-file mode and timestamps, disables xattr opflags, and installs the bad op tables. Later VFS operations consistently fail.

State and persistence: the bad state is in-memory only and represented by `inode->i_op == &bad_inode_ops`; it deliberately prevents future normal operation on that inode instance.

Dependencies and integration: exported to filesystems across the kernel; used in iget/read-inode failure paths and invalidated-inode checks.

Risks: callers must use this only for real unreadable/corrupt inodes, because it makes the object uniformly fail with I/O errors. New VFS inode operations need corresponding bad stubs to avoid accidental success.

Test signals: inject inode read I/O failures in filesystems; verify open, lookup, getattr, xattrs, ACLs, fiemap, and write-time updates all fail with `-EIO`; assert `is_bad_inode()` after `iget_failed()`.
