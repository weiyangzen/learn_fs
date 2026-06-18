# sources/distributed-fs/ceph-client/tools/testing/selftests/pidfd/pidfd_info_test.c

Purpose: tests `PIDFD_GET_INFO` reporting for live, exited, reaped, signaled, successful, thread-specific, exec-transition, and supported-mask cases.

Important APIs/functions: fixture creates four children covering killed-not-reaped, killed-reaped, successful-not-reaped, and successful-reaped states. Tests use `ioctl(PIDFD_GET_INFO)`, `poll()` pidfds, `sys_waitid(P_PIDFD/P_PID)`, `PIDFD_THREAD`, pthread helpers, socket synchronization, and `sys_execveat()` of `pidfd_exec_helper`.

Control flow: basic tests verify credentials are available before reap, exit info appears after reap when requested, and non-requested exit info yields `ESRCH` for reaped processes. `success_reaped_poll` checks `POLLIN|POLLHUP` on reaped pidfd. `thread_group` creates a thread that outlives the leader, verifies thread pidfd opening rules, delayed notification, info for leader/thread pidfds, then kills the group and checks exit status for all pidfds. `thread_group_exec` and `_exec_thread` validate pidfd notification and exit-info behavior when a non-leader thread execs and assumes the leader pid. Supported-mask tests verify `supported_mask` is returned alone or with other fields.

State and persistence: creates children, threads, pidfds, sockets, and execs helper. It kills and reaps processes in tests and teardown.

Dependencies/integration: requires pidfd `PIDFD_GET_INFO`, pidfs thread pidfds, clone3, pthreads, exec helper in cwd, and newer supported-mask fields.

Risks: very sensitive to kernel pid/thread lifecycle semantics. Poll timeouts comment says 5 seconds but uses 10000 ms. Missing helper binary breaks exec tests.

Test signals: kselftest assertions on mask bits, credential/exit availability, poll revents, pids, and wait status macros.
