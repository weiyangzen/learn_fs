# sources/distributed-fs/ceph-client/tools/testing/selftests/proc/proc-self-syscall.c

Purpose: verifies `/proc/self/syscall` reports the currently executing raw `read` syscall and its first arguments.

Important APIs and functions: `sys_read()` invokes `SYS_read` directly, avoiding libc wrappers. The test uses `open`, `snprintf`, `read`, `strncmp`, and errno-based skip on missing proc entry.

Control flow: open `/proc/self/syscall`, build the expected prefix containing syscall number, fd, target buffer pointer, and length, invoke raw read into that buffer, and compare the prefix.

State and persistence: no persistent state.

Dependencies and integration: depends on `/proc/self/syscall` support and architecture formatting of syscall arguments as hex. Missing file returns skip 4.

Risks and test signals: pointer formatting and syscall wrapper behavior are central. Failure points to stale or incorrectly formatted syscall reporting.
