# sources/distributed-fs/ceph-client/tools/testing/selftests/proc/proc-tid0.c

Purpose: stress test that `/proc/$pid/task` never contains a bogus task entry named `0` while a child rapidly creates and joins threads.

Important APIs and functions: uses `fork`, pthread `pthread_create`/`pthread_join`, `opendir`, `readdir`, `strcmp`, `alarm`, and signal handlers.

Control flow: child loops creating one thread at a time. Parent repeatedly scans `/proc/$child/task` for one second. If entry `"0"` appears, parent exits failure; otherwise SIGALRM exits success.

State and persistence: transient child process and thread churn only. `atexit` kills the child.

Dependencies and integration: depends on procfs task directory updates and pthread support.

Risks and test signals: one-second duration is probabilistic but focused on a historical race. Failure means proc task iteration exposed an invalid TID during thread lifecycle transitions.
