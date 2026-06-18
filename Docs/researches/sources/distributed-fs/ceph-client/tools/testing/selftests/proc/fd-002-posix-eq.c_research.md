# sources/distributed-fs/ceph-client/tools/testing/selftests/proc/fd-002-posix-eq.c

Purpose: verifies opening `/proc/self/fd/<fd>` and `/proc/thread-self/fd/<fd>` yields the same underlying file as the original fd.

Important APIs/types/functions: main uses `open()`, `fstat()`, and compares `st_dev`/`st_ino`.

Control flow: opens `/` as a directory fd, constructs both proc fd paths, opens them, stats all three descriptors, and asserts device/inode equality.

State and persistence behavior: opens three fds; no persistent filesystem changes.

Dependencies and integration points: requires procfs `self` and `thread-self` fd views.

Risks and test signals: only checks POSIX identity by dev/inode, not file flags or offsets. All failures are assertions.
