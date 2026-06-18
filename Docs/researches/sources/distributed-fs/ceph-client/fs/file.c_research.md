# sources/distributed-fs/ceph-client/fs/file.c

## Purpose

`sources/distributed-fs/ceph-client/fs/file.c` manages per-process `files_struct` descriptor tables and common fd lifecycle syscalls. It covers fdtable allocation/growth, descriptor bitmaps, close/close-range, RCU-safe file lookup, fd installation, duplication, close-on-exec, received-fd installation, and iteration. The complete 1533-line file was read for this report.

## Important APIs, Types, and Functions

Exported or syscall-facing APIs include `__file_ref_put()`, `dup_fd()`, `get_unused_fd_flags()`, `put_unused_fd()`, `fd_install()`, `close_fd()`, `close_range()`, `file_close_fd()`, `do_close_on_exec()`, `get_file_rcu()`, `get_file_active()`, `fget()`, `fget_raw()`, `fget_task()`, `fget_task_next()`, `fdget()`, `fdget_raw()`, `fdget_pos()`, `__f_unlock_pos()`, `set_close_on_exec()`, `get_close_on_exec()`, `replace_fd()`, `receive_fd()`, `receive_fd_replace()`, `dup3`, `dup2`, `dup`, `f_dupfd()`, and `iterate_fd()`. Core structures are `files_struct`, `fdtable`, `file_ref_t`, fd bitmaps, and `struct fd`.

## Control Flow

Fd allocation uses `alloc_fd()` to scan `open_fds` and `full_fds_bits`, expand tables under `files->file_lock` when necessary, mark the slot open, and leave `fdt->fd[fd]` NULL until `fd_install()`. Growth allocates a new fdtable outside the spinlock, synchronizes with lockless installers via RCU and barriers, copies descriptors/bitmaps, then publishes with `rcu_assign_pointer()`. Close paths clear the fd slot under the lock and then call `filp_close()` outside it. Duplication and replacement expand the table, get a reference on the source file, atomically replace the target slot, and close the displaced file after dropping the lock.

## State and Persistence Behavior

State is per-task or shared-thread-group runtime state, not file-backed persistence. `files_struct` carries an atomic share count, resize state, waitqueue, next-fd hint, embedded small fdtable, and optional expanded RCU-freed tables. `struct file` lifetimes are protected by file refcounts and SLAB_TYPESAFE_BY_RCU validation. Close-on-exec state is bitmap-backed and consumed by `do_close_on_exec()` during exec.

## Dependencies and Integration Points

This file integrates with syscall wrappers, `rlimit(RLIMIT_NOFILE)`, `sysctl_nr_open`, RCU, speculative-execution index masking, socket receive hooks, LSM `security_file_receive()`, `filp_close()`, process task locking, `close_range` unshare semantics, and the Rust file API expectations documented in comments.

## Risks and Edge Cases

The riskiest areas are fdtable resize/install races, reserved-but-uninstalled fd slots, RCU file reuse, descriptor-table sharing during close-range unshare, and memory ordering between reference acquisition and pointer validation. The code intentionally returns `-EBUSY` for `dup2` races against userspace fd reservation. Changes to barriers or bitmap invariants can become use-after-free, leaked file references, or fd aliasing bugs.

## Test Signals

Signals include LTP and kselftest coverage for `dup*`, `close_range`, `SCM_RIGHTS`, `pidfd_getfd`, exec close-on-exec, fd exhaustion, concurrent open/dup/close stress, KCSAN/lockdep for fdtable resize races, and syzkaller coverage for malformed fd inputs and shared `files_struct` corner cases.
