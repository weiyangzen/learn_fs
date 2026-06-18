# sources/distributed-fs/ceph-client/fs/fs_struct.c

## Purpose
`fs_struct.c` manages each task's filesystem view: root path, current working directory, umask, users count, and exec/unshare state. It supplies safe setters, cloning, unsharing, exit cleanup, and chroot reference updates across tasks.

## Important APIs, Types, and Functions
- `set_fs_root()` and `set_fs_pwd()` replace root/pwd with path refcounting under `fs->seq`.
- `chroot_fs_refs()` rewrites task `root`/`pwd` references from an old root to a new root.
- `free_fs_struct()`, `exit_fs()`, `copy_fs_struct()`, and `unshare_fs_struct()` own lifetime and copy-on-unshare behavior.
- `init_fs` is the initial boot-time `fs_struct`.

## Control Flow
Setters grab a reference on the new path, update the field under a seqlock writer section, then drop the old path. `chroot_fs_refs()` scans every process/thread under `tasklist_lock`, locks each task, replaces matching root/pwd paths under the target `fs_struct` seqlock, then balances old path references after the scan. `exit_fs()` clears `tsk->fs` and decrements `users`; the last user frees the structure. `copy_fs_struct()` snapshots root and pwd under the old seqlock and increments both path refs.

## State and Persistence
The state is entirely in-memory task state. Path objects are refcounted with `path_get()`/`path_put()`. `users` tracks sharing between threads or clone users. `seq` gives lockless path readers a consistency point.

## Dependencies and Integration Points
This code integrates with scheduler task locking, path refcounting, `tasklist_lock`, init task setup, chroot/pivot-root style operations, and clone/unshare/exit code. It is core VFS process state, not Ceph-specific despite residing in the source subset.

## Risks
The key risks are reference imbalance when replacing root/pwd, task iteration races, and seqlock misuse by readers. `chroot_fs_refs()` walks all tasks and can be expensive, but it is limited to rare namespace/root transitions. `exit_fs()` relies on taking task and fs locks in the established order.

## Test Signals
Regression signals include `chdir`, `chroot`, `pivot_root`, `unshare(CLONE_FS)`, thread sharing, exec, process exit under parallel cwd/root changes, path refcount leaks, and lockdep warnings.
