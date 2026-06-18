# sources/distributed-fs/ceph-client/fs/jfs/Makefile

## Purpose
Defines the Kbuild object composition for the JFS filesystem.

## Important APIs, types, and functions
`obj-$(CONFIG_JFS_FS) += jfs.o` builds the aggregate object. `jfs-y` lists core implementation objects including superblock, inode, VFS, xtree/dtree/imap/dmap, log/transaction, xattr, ioctl, resize, and discard. `acl.o` is conditional on `CONFIG_JFS_POSIX_ACL`.

## Control flow
Kbuild expands the object list after Kconfig resolution; source code assumes the base objects are linked into `jfs.o`.

## State and persistence behavior
No runtime state.

## Dependencies and integration points
Integrates with Kbuild and JFS Kconfig symbols.

## Risks and test signals
Run config-matrix builds to catch missing objects, stale symbols, and ACL enabled/disabled link failures.
