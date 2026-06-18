# sources/distributed-fs/ceph-client/fs/affs/super.c

## Purpose
`super.c` implements AFFS filesystem registration, mount option parsing, root block probing, format detection, bitmap initialization, superblock operations, delayed superblock timestamp flushing, remount handling, statfs, and teardown.

## Important APIs, types, and functions
Important functions include `affs_init_fs_context()`, `affs_parse_param()`, `affs_fill_super()`, `affs_reconfigure()`, `affs_mark_sb_dirty()`, `affs_commit_super()`, `affs_sync_fs()`, `affs_put_super()`, `affs_kill_sb()`, `affs_statfs()`, and module init/exit. `struct affs_context` holds parsed mount options.

## Control flow
Mount parses options such as `bs`, `mode`, `mufs`, `nofilenametruncate`, `prefix`, `protect`, `reserved`, `root`, `setuid`, `setgid`, `verbose`, and `volume`. It probes possible block sizes/root positions, validates root block checksum/type, reads the boot signature to detect OFS/FFS/INTL/MUFS/dircache variants, forces unsupported dircache writes read-only, initializes bitmap state, creates the root inode, selects dentry casefold ops, and installs export ops.

## State and persistence
Runtime superblock state includes root block buffer, bitmap cache, flags, UID/GID/mode overrides, symlink prefix/volume, delayed work, and locks. Persistent state touched here is the root block disk-change timestamp and checksum.

## Dependencies and integration points
It depends on block devices, fs_context, AFFS bitmap/inode code, workqueues, seq_file option display, and VFS mount/sync/statfs APIs.

## Risks and test signals
Risks include mount failure cleanup leaks, incorrect root-block detection on odd-sized partitions, dircache read/write policy, remount read/write bitmap transitions, delayed work after unmount, and symlink prefix races. Test signals include all supported boot signatures, explicit and probed block sizes, read-only dircache mounts, remount option changes, statfs free counts, delayed superblock flush, and module unload.
