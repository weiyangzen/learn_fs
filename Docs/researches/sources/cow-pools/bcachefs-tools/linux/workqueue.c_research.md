# File Research: sources/cow-pools/bcachefs-tools/linux/workqueue.c

## Purpose
Userspace workqueue/delayed-work implementation.

## Key Responsibilities
- Allocates named workqueues and starts worker kthreads lazily.
- Implements immediate and delayed work queueing.
- Supports flushing, canceling, modifying delayed work, draining, and destruction.
- Initializes global system workqueues in a constructor.

## Key APIs
- `queue_work()`
- `queue_delayed_work()`
- `mod_delayed_work()`
- `flush_work()`
- `cancel_work_sync()`
- `cancel_delayed_work()`, `cancel_delayed_work_sync()`
- `drain_workqueue()`
- `destroy_workqueue()`
- `alloc_workqueue()`

## Implementation Notes
- One global mutex serializes all workqueue state.
- Work pending state is stored in `WORK_PENDING_BIT`.
- Delayed work uses `timer_list`; timer callback enqueues the work.
- `grab_pending()` handles races between pending list, delayed timer, and running work.
- Constructor creates `system_wq`, `system_highpri_wq`, `system_long_wq`, `system_unbound_wq`, and `system_freezable_wq`.

## Dependencies
Uses local kthread, timer, workqueue, list, slab, and error-name helpers.
