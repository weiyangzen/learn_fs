# sources/distributed-fs/ceph-client/fs/statfs.c

## Purpose

`statfs.c` implements VFS filesystem-stat queries and the statfs/fstatfs/ustat syscall family, including native, 64-bit, and compat ABI conversions.

## Important APIs, Types, and Functions

Public helpers are `vfs_get_fsid()`, `vfs_statfs()`, `user_statfs()`, and `fd_statfs()`. Internal helpers include `flags_by_mnt()`, `flags_by_sb()`, `calculate_f_flags()`, `statfs_by_dentry()`, `do_statfs_native()`, `do_statfs64()`, `vfs_ustat()`, and compat copy/syscall helpers.

## Control Flow

Path-based syscalls resolve a pathname with follow/automount lookup flags and retry on stale dentries. FD-based syscalls get the file path from the descriptor. Both call `vfs_statfs()`, which invokes the filesystem `statfs` super operation after `security_sb_statfs()` and then fills mount/superblock flags. ABI helpers copy `kstatfs` into user layouts with overflow checks where fields may be narrower.

## State and Persistence Behavior

The code returns snapshots of superblock and mount state. It does not mutate filesystem state. `f_flags` is synthesized from mount and superblock flags for each query.

## Dependencies and Integration Points

It integrates with VFS path/fd lookup, superblock `s_op->statfs`, LSM security hooks, user copy, compat syscall tables, `user_get_super()` for `ustat`, and mount flag definitions.

## Risks and Edge Cases

Filesystems without `statfs` return `-ENOSYS`. 32-bit ABI overflow detection must handle fields where `-1` is an accepted sentinel for files/free files. `statfs64` size arguments must match the ABI struct size. Stale path retry behavior matters for network filesystems.

## Test Signals

LTP statfs/fstatfs/ustat tests, compat syscall tests, mount flag visibility tests, overflow cases with huge filesystems, security hook denial tests, and filesystems with missing or custom `statfs`.
