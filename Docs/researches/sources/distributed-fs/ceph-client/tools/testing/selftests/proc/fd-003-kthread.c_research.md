# sources/distributed-fs/ceph-client/tools/testing/selftests/proc/fd-003-kthread.c

Purpose: tests that `/proc/<kernel-thread>/fd/` is empty and rejects numeric fd lookups.

Important APIs/types/functions: `kernel_thread_fd()` identifies kernel threads by parsing `/proc/<pid>/stat` flags for `PF_KHTREAD`; `test_readdir()` checks only `.` and `..`; `test_lookup()` uses `statx` to verify ENOENT for many names.

Control flow: starting at pid 2, the program scans pids below 1024 until it can open an fd directory for a kernel thread. It then validates directory entries and negative/overflow fd lookup rejection.

State and persistence behavior: opens procfs descriptors only. No process or kernel state is changed.

Dependencies and integration points: depends on procfs exposing task flags in stat, accessible kernel thread proc entries, and `SYS_statx`.

Risks and test signals: typo `PF_KHTREAD` names the kernel-thread flag constant locally but value is what matters. Non-root or hidepid settings may prevent finding a suitable pid, returning failure.
