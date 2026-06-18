# File Research: sources/cow-pools/bcachefs-tools/include/linux/kthread.h

This header declares kernel-thread compatibility APIs and kthread workqueue structures. `kthread_create()`, `kthread_create_on_cpu()`, stop/park/query helpers, and data accessors are declared externally. `kthread_run()` wraps create plus `wake_up_process()` unless creation returned an error pointer.

It defines `struct kthread_worker` and `struct kthread_work`, initialization macros, worker/work definitions, `init_kthread_worker()`, `init_kthread_work()`, and queue/flush function declarations. The implementation is elsewhere, likely backed by pthread/task shims.
