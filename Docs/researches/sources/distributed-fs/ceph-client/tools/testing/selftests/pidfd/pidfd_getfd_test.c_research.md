# sources/distributed-fs/ceph-client/tools/testing/selftests/pidfd/pidfd_getfd_test.c

Purpose: tests `pidfd_getfd()` for fetching a target process fd, permission denial, invalid flags, unknown fd, and a historical exiting-task race that should return `ESRCH` instead of misleading `EBADF`.

Important APIs/functions: local `sys_kcmp()` compares file identity; child helper creates a memfd and reports its fd number over a socketpair; fixture opens a pidfd for the child and keeps a control socket. Tests use `prctl(PR_SET_DUMPABLE, 0)` to disable ptrace access, `seteuid(65535)` when root, `sys_pidfd_getfd()`, `fcntl(F_GETFD)`, `poll()` on pidfd, and `KCMP_FILE`.

Control flow: fixture forks child, waits for remote memfd number, and opens pidfd. `disable_ptrace` commands child to disable dumpability and expects `EPERM`. `fetch_fd` gets the fd and verifies same underlying file through `kcmp()` unless unsupported. `test_unknown_fd` expects `EBADF`. `flags_set` expects `EINVAL` for nonzero flags. `no_strange_EBADF` kills child, waits for pidfd readability, and expects `ESRCH` when fetching from an exited task.

State and persistence: creates socketpair, child process, memfd, pidfd, and temporary fetched fd. No files persist.

Dependencies/integration: requires pidfd_getfd syscall, pidfd_open, memfd_create, ptrace permission checks, optional kcmp, and local UNIX sockets.

Risks: permission behavior depends on credentials/capabilities. `kcmp()` may be unavailable and is skipped. The race regression test depends on timing but polls for exit before fetching.

Test signals: kselftest harness; compile-time fallback main returns skip if `__NR_pidfd_getfd` is unavailable.
