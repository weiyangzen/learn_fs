# File Research: sources/cow-pools/bcachefs-tools/include/linux/workqueue.h

Declares kernel-like workqueue structures and APIs. It defines `work_struct`, `delayed_work`, initialization macros, pending checks, workqueue flags, system workqueues, allocation/destruction, queue/flush/cancel functions, and schedule wrappers.

Implementation in `linux/workqueue.c` uses pthread mutex/cond plus lazily-created kthread workers.
