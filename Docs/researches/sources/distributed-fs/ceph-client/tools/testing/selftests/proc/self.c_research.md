# sources/distributed-fs/ceph-client/tools/testing/selftests/proc/self.c

Purpose: verifies `/proc/self` readlink resolves to the caller's thread-group ID.

Important APIs and functions: uses `sys_getpid()` from `proc.h`, `snprintf`, `readlink`, `strlen`, and `streq`.

Control flow: format the current PID as decimal, read `/proc/self`, NUL-terminate the link target, and compare exactly.

State and persistence: none.

Dependencies and integration: depends on procfs self symlink behavior.

Risks and test signals: failure means `/proc/self` is resolving to the wrong pid namespace identity or formatting changed.
