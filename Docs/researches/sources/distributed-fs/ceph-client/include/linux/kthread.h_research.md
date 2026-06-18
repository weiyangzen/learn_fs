# sources/distributed-fs/ceph-client/include/linux/kthread.h

## Purpose

`kthread.h` declares the kernel thread creation, binding, stopping, parking, freezer, worker, delayed-work, mm borrowing, and block-cgroup association APIs. The source was read as a complete 293-line file.

## Important APIs, Types, and Functions

Important APIs include `tsk_is_kthread()`, `kthread_create_on_node()`, `kthread_create()`, `kthread_create_on_cpu()`, `kthread_run()`, `kthread_run_on_cpu()`, `kthread_bind()`, `kthread_stop()`, `kthread_stop_put()`, `kthread_should_stop()`, `kthread_should_park()`, `kthread_freezable_should_stop()`, `kthread_park()`, `kthread_unpark()`, `kthread_parkme()`, `kthread_complete_and_exit()`, `kthread_worker_fn()`, `kthread_create_worker_on_node()`, `kthread_run_worker()`, `kthread_queue_work()`, `kthread_queue_delayed_work()`, `kthread_mod_delayed_work()`, `kthread_flush_work()`, `kthread_cancel_work_sync()`, `kthread_destroy_worker()`, `kthread_use_mm()`, and `kthread_unuse_mm()`. Types include opaque `struct kthread`, `struct kthread_worker`, `struct kthread_work`, and `struct kthread_delayed_work`.

## Control Flow

Creation helpers allocate a stopped task, set kthread-private state, optionally bind it, and callers wake it. Thread functions loop until stop/park/freezer helpers indicate state changes. Worker APIs queue work under raw spinlock and a kthread executes each work function; delayed work uses timers.

## State and Persistence Behavior

Kthread state is attached to `task_struct->worker_private` when `PF_KTHREAD` is set. Worker state includes work lists, delayed list, current work, and task pointer. State persists until stopped/destroyed.

## Dependencies and Integration Points

It integrates with scheduler tasks, NUMA/CPU affinity, completions, timers, raw spinlocks, freezer, housekeeping CPUs, mm borrowing, and blk-cgroup association.

## Risks and Edge Cases

Created threads are stopped until woken. Stop/park protocols require cooperative checks by the thread. Delayed work cancellation races must use sync helpers. Borrowed mm and blkcg association must be undone appropriately. CPU-bound name format is restricted.

## Test Signals

Kthread lifecycle tests, stop/park/freezer tests, CPU binding tests, worker queue/flush/cancel tests, delayed work timer tests, mm borrow tests, blkcg association tests, and module unload races are useful.
