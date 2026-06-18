# sources/distributed-fs/ceph-client/include/linux/fdtable.h

## Purpose

`sources/distributed-fs/ceph-client/include/linux/fdtable.h` defines internal file descriptor table structures and lookup helpers. The source was read as a complete 118-line file for this report.

## Important APIs, Types, and Functions

Important exports are `NR_OPEN_DEFAULT`, `struct fdtable`, `struct files_struct`, `rcu_dereference_check_fdtable`, `files_fdtable`, `files_lookup_fd_raw`, `files_lookup_fd_locked`, `close_on_exec`, `put_files_struct`, `unshare_files`, `struct fd_range`, `dup_fd`, `do_close_on_exec`, `iterate_fd`, `close_fd`, `file_close_fd`, and `files_cachep`.

## Control Flow

VFS fd operations use `files_struct` as the per-task descriptor table. Lookups read the RCU-protected `fdtable`, use `array_index_mask_nospec()` to guard bounds/speculation, and return masked file pointers. Writers hold `file_lock`, resize tables, set close-on-exec/open/full bitmaps, and duplicate or close descriptor ranges.

## State and Persistence Behavior

`files_struct` persists while shared by tasks through an atomic count. It stores the active fdtable pointer, inline default arrays, descriptor bitmaps, `next_fd`, resize state, lock, and wait queue. State is process runtime state, not file-backed.

## Dependencies and Integration Points

It depends on RCU, spinlocks, nospec helpers, fs types, and atomics. It integrates with fork/clone/unshare, exec close-on-exec, file lookup, close, descriptor iteration, and VFS file lifetime.

## Risks and Edge Cases

RCU and locking rules are strict. Out-of-range fd access must remain speculation-safe. Resize and shared `files_struct` operations can race with lookups if callers do not hold RCU or `file_lock` as required.

## Test Signals

fdtable stress tests with concurrent open/close/dup/exec/fork, KCSAN/lockdep coverage, close-on-exec tests, and Spectre/nospec regression tests for fd lookups.
