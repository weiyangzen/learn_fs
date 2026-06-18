# sources/distributed-fs/ceph-client/tools/testing/selftests/pidfd/pidfd_test.c

## Purpose
Provides a broader pidfd regression binary for signal delivery, pid reuse safety, and pidfd poll behavior when thread-group leaders exec or exit while other threads exist.

## Important APIs, Types, and Functions
Important functions are `pidfd_clone()`, `send_signal()`, `send_signal_worker()`, `test_pidfd_send_signal_*()`, `poll_pidfd()`, `test_pidfd_poll_exec()`, `test_pidfd_poll_leader_exit()`, and `main()`. It uses `PIDFD_SELF_THREAD`, `PIDFD_SELF_THREAD_GROUP`, `CLONE_PIDFD`, epoll, pthreads, `mmap()` shared state, and namespace/mount syscalls.

## Control Flow
`main()` declares eight kselftest results, runs poll timing tests with pidfd and waitpid baselines, probes pidfd_send_signal support, sends SIGUSR1 to self and a worker thread, verifies signaling an exited process returns `ESRCH`, then attempts a pid-recycle scenario inside a new pid namespace to ensure old pidfds cannot signal a new task with the same numeric pid.

## State and Persistence
State includes global pidfd_send_signal support, thread-local signal observation, shared `child_exit_secs`, child namespaces, temporary proc remounting inside a child, and process/thread lifetimes. No durable files are created outside transient namespace mount changes.

## Dependencies and Integration Points
Depends on `pidfd.h`, kselftest, pthreads, epoll, clone, pid namespaces, procfs, and `/bin/sleep` for exec timing. It integrates user-visible pidfd semantics with scheduler/thread-group behavior.

## Risks and Test Signals
Timing windows are deliberate: poll must not report too early when a non-leader thread execs or when the leader exits while other threads run. Environment risks include missing pid namespaces, high `pid_max`, absent pidfd_send_signal, or scheduler delays outside the 3 to 5 second expected windows.
