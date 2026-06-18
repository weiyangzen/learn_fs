# sources/distributed-fs/ceph-client/tools/testing/selftests/tty/tty_tiocsti_test.c

## Purpose
This kselftest harness validates `TIOCSTI` input injection behavior across the `dev.tty.legacy_tiocsti` sysctl, `CAP_SYS_ADMIN`, controlling-terminal status, and file descriptor passing via `SCM_RIGHTS`. It also demonstrates the credential model where the current process credentials, not opener credentials, control injection permission.

## Important APIs, Types, and Functions
The file uses `kselftest_harness.h` fixtures and variants. Helpers include `send_fd_via_socket()`, `recv_fd_via_socket()`, `has_cap_sys_admin()`, `drop_all_privs()`, `get_legacy_tiocsti_setting()`, `set_legacy_tiocsti_setting()`, `test_tiocsti_injection()`, `run_basic_tiocsti_test()`, and `run_fdpass_tiocsti_test()`. It uses `openpty()`, `ioctl(TIOCSTI)`, `ioctl(TIOCSCTTY)`, `socketpair()`, `sendmsg/recvmsg(SCM_RIGHTS)`, `cap_get_proc()`, `cap_set_proc()`, `setuid/setgid`, and `prctl(PR_SET_NO_NEW_PRIVS)`.

## Control Flow
Fixture variants enumerate basic PTY tests and FD-passing tests for controlling and non-controlling terminals, permissive/restricted sysctl settings, and with/without `CAP_SYS_ADMIN`. Setup creates a PTY, reads/restores the sysctl, checks initial capabilities, and skips unsupported combinations. The single fixture test forks: basic mode performs injection in the child after optional privilege drop and optional controlling-terminal setup; FD-passing mode has the child create/pass a PTY slave FD and the privileged parent attempts injection through the received FD.

## State and Persistence
The fixture temporarily changes `/proc/sys/dev/tty/legacy_tiocsti` and restores it in teardown. Children may create sessions, controlling terminals, PTYs, and dropped credentials. File descriptors are closed in normal paths.

## Dependencies and Integration Points
It depends on libcap, PTYs, Unix domain sockets, root/CAP_SYS_ADMIN for several variants, kernel sysctl `dev.tty.legacy_tiocsti`, and the kselftest harness.

## Risks
The test assumes uid/gid 1000 exist for privilege dropping. Missing sysctl or insufficient permission causes skips. Because it forks and manipulates sessions/controlling terminals, assertion failures in children are reported through wait status. The FD-passing cases intentionally exercise a security-sensitive behavior and require careful interpretation of expected success.

## Test Signals
Expected results are exact `0`, `-EIO`, or `-EPERM` outcomes from `ioctl(TIOCSTI)`. Passing means the kernel enforces legacy sysctl and capability/controlling-terminal checks exactly as represented by the matrix, including current-credential behavior after FD passing.
