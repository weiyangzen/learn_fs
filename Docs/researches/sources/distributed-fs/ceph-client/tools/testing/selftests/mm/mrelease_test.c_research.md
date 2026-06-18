# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/mrelease_test.c

## Purpose

`mrelease_test.c` tests `process_mrelease()` on a killed child process and validates negative cases for bad pidfds, invalid flags, and live processes without pending `SIGKILL`.

## Important APIs, Types, and Functions

The file uses `pidfd_open`, `process_mrelease`, `kill(SIGKILL)`, `waitpid()`, pipes, `mmap()`, and `psize()` from `vm_util.h`. Helpers are `alloc_noexit()`, `run_negative_tests()`, and `child_main()`.

## Control Flow

`main()` first checks `process_mrelease(-1, 0)` returns `EBADF` or skips on `ENOSYS`. It forks a child that allocates and faults a configurable amount of memory, signals readiness through a pipe, and waits to be killed. The parent obtains a pidfd, runs negative tests while the child is alive, sends `SIGKILL`, calls `process_mrelease(pidfd, 0)`, waits for the child, and retries with doubled memory if the child exited too quickly and `ESRCH` was returned.

## State and Persistence Behavior

Child memory is anonymous and transient. The parent creates pidfds and pipes and closes them after each attempt. The retry loop increases child allocation from 1 MiB up to 1024 MiB to widen the window for successful release.

## Dependencies and Integration Points

It depends on `__NR_process_mrelease`, `__NR_pidfd_open`, Linux pidfd semantics, and mm process teardown. It integrates with userspace OOM-killer style memory reaping.

## Risks and Edge Cases

The positive case is inherently racy because `process_mrelease()` must run after `SIGKILL` but before the process fully exits. The retry logic handles `ESRCH` only; other failures are fatal. Memory allocation can grow to 1 GiB, which may be expensive on constrained systems.

## Test Signals

Success is one planned pass result reporting the allocation size at which child memory was reaped. Skips occur when the syscall is not implemented.
