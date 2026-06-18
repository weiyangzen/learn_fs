# sources/distributed-fs/ceph-client/fs/btrfs/ioctl.h

## Purpose
`ioctl.h` is the private declaration boundary for Btrfs ioctl and file-attribute helpers. It lets inode/file operation tables, io_uring command paths, and other Btrfs modules call the implementation in `ioctl.c` without exposing implementation details. The source was read as a complete 29-line header.

## Important APIs, Types, and Functions
The header forward-declares kernel and Btrfs types used by the prototypes: `struct file`, `dentry`, `mnt_idmap`, `file_kattr`, `io_uring_cmd`, `btrfs_inode`, `btrfs_fs_info`, and `btrfs_ioctl_balance_args`. It declares `btrfs_ioctl()`, `btrfs_compat_ioctl()`, `btrfs_fileattr_get()`, `btrfs_fileattr_set()`, `btrfs_ioctl_get_supported_features()`, `btrfs_sync_inode_flags_to_i_flags()`, `btrfs_update_ioctl_balance_args()`, `btrfs_uring_cmd()`, and `btrfs_uring_read_extent_endio()`.

## Control Flow
There is no independent runtime flow. The prototypes connect VFS file operations and io_uring command dispatch to `ioctl.c`, and allow shared helpers such as inode flag synchronization and balance-argument reporting to be reused elsewhere.

## State and Persistence Behavior
The header defines no state. It advertises functions that may alter persistent filesystem metadata, inode state, or async I/O command state in the implementation.

## Dependencies and Integration Points
The only direct include is `<linux/types.h>`. The declarations integrate with Btrfs inode operations, file operations, balance code, and io_uring command handling.

## Risks and Edge Cases
Prototype drift here would break cross-module builds or cause mismatches in compat/io_uring call signatures. The `void __user *` prototype for supported features preserves UAPI-copy semantics from the implementation.

## Test Signals
Build coverage with Btrfs, compat ioctl, fileattr, and io_uring enabled is the main signal. Runtime coverage comes through the `ioctl.c` tests for each declared operation.
