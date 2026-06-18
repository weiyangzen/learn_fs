# sources/distributed-fs/ceph-client/tools/testing/selftests/proc/proc-2-is-kthread.c

Purpose: verifies procfs reports pid 2 (`kthreadd`) as a kernel thread via `/proc/2/status`.

Important APIs/types/functions: main opens `/proc/2/status`, reads it into a buffer, and asserts it contains `Kthread:	1
`.

Control flow: single open/read/string-search sequence with assertions.

State and persistence behavior: read-only procfs access; no persistent state.

Dependencies and integration points: assumes pid 2 is kthreadd and procfs status includes the Kthread field.

Risks and test signals: containers, pid namespaces, hidepid, or kernels without the field can fail the test even if procfs fd behavior is otherwise correct.
