# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/ptrace/child.h

## Purpose
`child.h` provides semaphore-based parent/child synchronization helpers for powerpc ptrace tests, including fail/skip macros that wake the other side before exiting.

## Important APIs, Types, and Functions
It defines `struct child_sync`, `CHILD_FAIL_IF`, `PARENT_FAIL_IF`, `PARENT_SKIP_IF_UNSUPPORTED`, `init_child_sync()`, `destroy_child_sync()`, `wait_child()`, `prod_child()`, `wait_parent()`, and `prod_parent()`.

## Control Flow and State
Initialization creates two process-shared semaphores and clears give-up flags. Parent and child alternate wait/post operations; fail macros set the appropriate flag and post the peer so tests do not deadlock. State is held in shared memory containing semaphores and flags.

## Dependencies and Integration Points
The header depends on POSIX semaphores and kselftest macros from `ptrace.h`/utils users. It is used by pkey core/ptrace tests that coordinate register reads while the child changes access rights.

## Risks and Test Signals
Risks are process-shared semaphore failures, missed wakeups on early exit, and tests forgetting to destroy semaphores. Signals are deterministic parent/child progress and clean skip/fail propagation.
