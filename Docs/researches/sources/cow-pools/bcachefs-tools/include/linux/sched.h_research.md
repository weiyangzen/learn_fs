# File Research: sources/cow-pools/bcachefs-tools/include/linux/sched.h

Declares the userspace `task_struct` shim, task states, process flags, `current` TLS pointer, task refcount helpers, scheduling APIs, wakeup API, monotonic/realtime helpers, and stack trace hook.

It backs pthread-based kthreads and futex-based scheduling in `linux/kthread.c` and `linux/sched.c`. Many kernel flags are retained for source compatibility even when only a subset has userspace behavior.
