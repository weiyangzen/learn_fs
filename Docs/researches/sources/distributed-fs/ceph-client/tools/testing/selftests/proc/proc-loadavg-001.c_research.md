# sources/distributed-fs/ceph-client/tools/testing/selftests/proc/proc-loadavg-001.c

Purpose: verifies that the last PID field in `/proc/loadavg` is reported relative to the current PID namespace.

Important APIs and functions: uses `unshare(CLONE_NEWPID)`, `fork`, `waitpid`, `open`, `read`, and `lseek`. The parsing is deliberately minimal, checking the final `" 1\n"` and `" 2\n"` suffixes.

Control flow: the parent enters a new PID namespace and forks the namespace init. The child reads `/proc/loadavg`, requires last pid 1, forks and waits for one child, rewinds the fd, reads again, and requires last pid 2.

State and persistence: uses transient namespace process state only. The proc file descriptor is reused across reads.

Dependencies and integration: requires PID namespace support and permission to create one. `ENOSYS` or `EPERM` returns kselftest skip 4.

Risks and test signals: parsing assumes the last pid remains a one-digit suffix for this small namespace. Failure points to incorrect pid namespace scoping in loadavg or broken proc file seek/read behavior.
