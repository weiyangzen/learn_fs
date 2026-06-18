# sources/distributed-fs/ceph-client/tools/testing/selftests/ptrace/vmaccess.c

Purpose: regression tests for `/proc/$pid/mem` and ptrace attach behavior while a multithreaded child is in a de_thread/exec transition with `cred_guard_mutex` held.

Important APIs and functions: kselftest harness tests `vmaccess` and `attach`; helper thread calls `ptrace(PTRACE_TRACEME)`. Uses `fork`, pthreads, `execlp`, open `/proc/$pid/mem`, `PTRACE_ATTACH`, `PTRACE_DETACH`, `kill(SIGCONT)`, and wait status checks.

Control flow: first test forks a child that creates a traced thread and execs `true`; parent sleeps, opens `/proc/$pid/mem`, closes it, and resumes child. Second test expects early `PTRACE_ATTACH` to fail with `EAGAIN`, observes an intermediate child exit, then later attaches to the execed sleep process and detaches cleanly.

State and persistence: transient child process/thread states only.

Dependencies and integration: depends on ptrace restrictions and timing around exec/de_thread.

Risks and test signals: `sleep(1)` timing is heuristic. Failures may signal deadlock regressions, incorrect EAGAIN handling, or task lifetime changes.
