# sources/distributed-fs/ceph-client/include/linux/filelock.h

## Purpose

`sources/distributed-fs/ceph-client/include/linux/filelock.h` defines VFS file lock, flock, lease, delegation, and lock-manager interfaces. It includes a Ceph-specific private lock union member. The source was read as a complete 596-line file for this report.

## Important APIs, Types, and Functions

Important flags include `FL_POSIX`, `FL_FLOCK`, `FL_DELEG`, `FL_LEASE`, `FL_CLOSE`, `FL_SLEEP`, `FL_OFDLCK`, `FL_LAYOUT`, and `FILE_LOCK_DEFERRED`. Key types are `struct file_lock_operations`, `struct lock_manager_operations`, `struct lease_manager_operations`, `struct lock_manager`, `struct file_lock_core`, `struct file_lock`, `struct file_lease`, `struct file_lock_context`, and `struct delegated_inode`. APIs include fcntl lock/lease/delegation helpers, `locks_start_grace`, `locks_end_grace`, `locks_in_grace`, `opens_in_grace`, lock classification helpers, lock allocation/copy/free/remove/test functions, `posix_lock_file`, `vfs_lock_file`, `vfs_cancel_lock`, lease break/set/modify helpers, `show_fd_locks`, `locks_inode_context`, `break_lease`, `break_deleg`, `try_break_deleg`, `break_deleg_wait`, and `break_layout`.

## Control Flow

fcntl and flock syscalls build `file_lock` requests, test conflicts, enqueue blocking locks, wake waiters, or dispatch to filesystem/lock-manager callbacks. Lease/delegation paths check inode lock contexts, use memory barriers around lockless lease-list tests, and call `__break_lease()` for blocking or nonblocking break flows. Disabled `CONFIG_FILE_LOCKING` builds return errors or no-op fallbacks.

## State and Persistence Behavior

`file_lock_context` hangs off inodes and stores flock, POSIX, and lease lists under a spinlock. Each lock tracks owner, type, range, pid, file, waitqueue, blocker, blocked requests, global-list linkage, and filesystem-private state. The union includes NFS/NFSv4, AFS, and Ceph `struct inode *` private state.

## Dependencies and Integration Points

It includes `linux/fs.h` and `linux/nfs_fs_i.h`. Integration points include VFS fcntl/flock, NFS/NLM/NFSv4 lock managers, AFS, Ceph, pNFS layouts, leases/delegations, proc lock display, inode operation flags, and network namespace grace periods.

## Risks and Edge Cases

Lock objects can be requests or granted locks, but never both. List ordering by owner/range matters for POSIX semantics. Lockless lease checks require the paired acquire/release barriers. Ceph lock private state must remain compatible with generic copy/release flows.

## Test Signals

POSIX and OFD lock tests, flock tests, lease/delegation break tests, network lock manager grace-period tests, CephFS lock recovery tests, `/proc/locks` tests, lockdep/KCSAN, and disabled-config build tests.
