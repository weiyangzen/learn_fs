# sources/distributed-fs/ceph-client/tools/testing/selftests/pid_namespace/regression_enomem.c

Purpose: regression test for PID namespace init death semantics and pid reservation error reporting. It expects a second fork in a PID namespace whose init has exited to fail with `ENOMEM`.

Important APIs/functions: single kselftest `TEST(regression_enomem)` uses optional `unshare(CLONE_NEWUSER)`, `unshare(CLONE_NEWPID)`, `fork()`, and shared `wait_for_pid()`.

Control flow: if unprivileged, first enters a user namespace. Then it unshares a new PID namespace, forks a child that exits successfully and is waited. A subsequent `fork()` is expected to fail with `errno == ENOMEM`, matching kernel behavior when the namespace's init process is gone.

State and persistence: namespace and child process state only; no files.

Dependencies/integration: requires user/PID namespaces and correct kernel fork error behavior.

Risks: container policy can block namespace creation. The expected `ENOMEM` is kernel-specific semantic behavior and should not be generalized to ordinary fork failures.

Test signals: kselftest pass on expected failure; assertion failure if second fork succeeds or reports a different errno.
