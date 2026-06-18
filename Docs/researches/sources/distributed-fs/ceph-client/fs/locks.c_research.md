# sources/distributed-fs/ceph-client/fs/locks.c

## Purpose

`sources/distributed-fs/ceph-client/fs/locks.c` is the core VFS file locking implementation. It supports POSIX byte-range locks, BSD `flock` locks, open-file-description locks, leases, delegations, layout leases, blocked-lock dependency trees, deadlock detection, syscalls/fcntl entry points, lease break handling, `/proc/locks`, and exported helpers used by network lock managers such as lockd. The source was read as a complete 3097-line file for this report.

## Important APIs, Types, and Functions

Key exported APIs include `locks_alloc_lock`, `locks_alloc_lease`, `locks_release_private`, `locks_owner_has_blockers`, `locks_free_lock`, `locks_free_lease`, `locks_init_lock`, `locks_init_lease`, `locks_copy_conflock`, `locks_copy_lock`, `posix_test_lock`, `posix_lock_file`, `lease_modify`, `__break_lease`, `lease_get_mtime`, `generic_setlease`, `lease_register_notifier`, `lease_unregister_notifier`, `kernel_setlease`, `vfs_setlease`, `locks_lock_inode_wait`, `vfs_test_lock`, `vfs_lock_file`, `locks_remove_posix`, `vfs_cancel_lock`, and `vfs_inode_has_locks`. User entry points include `SYSCALL_DEFINE2(flock)`, `fcntl_getlk`, `fcntl_setlk`, and 32-bit `fcntl_getlk64`/`fcntl_setlk64` where applicable. Important state includes per-inode `file_lock_context`, per-CPU `file_lock_list`, `file_rwsem`, `blocked_hash`, `blocked_lock_lock`, kmem caches, lease sysctls, and the lease notifier chain.

## Control Flow

Lock operations allocate or initialize a `file_lock`, translate user `flock` structures into VFS ranges and owners, run security checks, then call `vfs_lock_file`. The generic POSIX path creates an inode lock context if needed, checks conflicts, optionally adds blocked requests with deadlock detection, merges adjacent same-owner locks, splits/downgrades replaced ranges, wakes blocked trees, and disposes removed locks. The flock path is whole-file and file-owner based. Lease operations add or modify lease records, notify on conflicting opens, break or downgrade leases with signals/callbacks, and optionally wait for break completion. Close paths remove POSIX, OFD, flock, and lease state. `/proc/locks` iterates global per-CPU lock lists and blocked dependency trees.

## State and Persistence Behavior

All state is in memory and attached to inodes, files, or global lock lists. `file_lock_context` persists while the inode lives and is freed with leak checks. Active locks and leases are stored on context lists and mirrored on global lists for `/proc/locks`; blocked waiters are linked beneath blockers and in `blocked_hash` for deadlock detection. There is no disk persistence; locks vanish with file close, process/file-owner cleanup, inode teardown, or filesystem/network-manager cleanup.

## Dependencies and Integration Points

The file integrates with LSM via `security_file_lock`, filesystem `file_operations->lock`, `->flock`, and `->setlease`, signal/fasync ownership for leases, procfs/seq_file, trace events from `trace/events/filelock.h`, sysctl, pid namespaces, SRCU notifiers, and network lock managers through `lock_manager_operations` hooks such as `lm_notify`, `lm_grant`, `lm_get_owner`, and `lm_put_owner`.

## Risks and Edge Cases

Concurrency is the main risk: `flc_lock`, `blocked_lock_lock`, `file_rwsem`, per-CPU list locks, and inode/file locks have strict roles. POSIX range updates must handle EOF, negative lengths, splitting into two locks, merging, and close/fcntl races. Deadlock detection is bounded and skipped for OFD locks. Async filesystem locks may return `FILE_LOCK_DEFERRED` only under documented conditions, and lock managers must later call `lm_grant`. Lease break timeouts can downgrade or remove leases. `/proc/locks` must traverse while preserving consistency and avoiding invisible PIDs.

## Test Signals

Run LTP/flock/fcntl/OFD lock suites, multithreaded range merge/split/unlock tests, deadlock-detection tests, close/fcntl race tests, filesystem `->lock` async/deferred tests with lockd, lease acquisition and break tests for read/write/delegation/layout leases, `/proc/locks` formatting tests across pid namespaces, kmemleak/KASAN lock lifecycle runs, and sysctl coverage for lease enable/break-time.
