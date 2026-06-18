# sources/distributed-fs/ceph-client/tools/testing/selftests/pidfd/pidfd_open_test.c

Purpose: tests `pidfd_open()` argument validation and basic `PIDFD_GET_INFO` consistency with `/proc/self/fdinfo`.

Important APIs/functions: `safe_int()`, whitespace trimming helpers, and `get_pid_from_fdinfo_file()` parse `Pid:` from fdinfo robustly. `main()` uses `sys_pidfd_open()`, `ioctl(PIDFD_GET_INFO)`, and credential getters.

Control flow: plan has four tests. It rejects invalid pid `-1`, rejects invalid nonzero flags, opens a pidfd for `getpid()`, parses fdinfo pid, then requests `PIDFD_INFO_CGROUPID` and validates returned pid, ppid, real/effective/saved/fs uid/gid fields, and nonzero cgroupid when the mask says it is present.

State and persistence: opens one pidfd and reads procfs fdinfo. No persistent state.

Dependencies/integration: requires pidfd_open, pidfs info ioctl, procfs fdinfo, and kselftest output.

Risks: the ppid mismatch diagnostic prints the wrong first variable in one message, but the comparison is correct. Credential expectations assume no concurrent credential changes.

Test signals: kselftest pass lines for invalid pid, invalid flags, open pidfd, and info validation; any validation error exits fail.
