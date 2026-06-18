# sources/distributed-fs/ceph-client/tools/testing/selftests/pidfd/pidfd_wait.c

## Purpose
Validates `waitid(P_PIDFD, ...)` semantics for normal exit, stopped/continued/killed states, and nonblocking pidfds.

## Important APIs, Types, and Functions
Uses `ptr_to_u64()`, `sys_clone3()` with `CLONE_PIDFD | CLONE_PARENT_SETTID`, `sys_waitid()`, `sys_pidfd_send_signal()`, `fcntl()` flag checks, and three harness tests: `wait_simple`, `wait_states`, and `wait_nonblock`.

## Control Flow
`wait_simple` rejects non-child and non-pidfd descriptors, then waits on a clone3 child pidfd. `wait_states` drives a child through SIGSTOP, SIGCONT, a second stop, and SIGKILL via pidfd. `wait_nonblock` verifies `ECHILD` for non-child self pidfd, `EAGAIN` without WNOHANG for a live child, zero with WNOHANG, and normal behavior after clearing O_NONBLOCK.

## State and Persistence
State is per-test child process state plus pipe synchronization and pidfd file status flags. No persistent storage is used.

## Dependencies and Integration Points
Depends on clone3, pidfd_open with `PIDFD_NONBLOCK`, pidfd_send_signal, waitid pidfd support, and `kselftest_harness.h`.

## Risks and Test Signals
The tests encode precise errno/si_code expectations (`CLD_EXITED`, `CLD_STOPPED`, `CLD_CONTINUED`, `CLD_KILLED`). Kernels lacking nonblocking pidfd support are skipped via the local `SKIP`/`XFAIL` compatibility macro.
