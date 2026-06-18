<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_preempt_fence.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_preempt_fence.c

## Purpose

`xe_preempt_fence.c` implements a Xe-specific `dma_fence` used to preempt or suspend an execution queue and signal once the queue is quiesced enough for VM rebinding.

## Important APIs and Functions

Public helpers are `xe_preempt_fence_alloc()`, `xe_preempt_fence_free()`, `xe_preempt_fence_arm()`, `xe_preempt_fence_create()`, and `xe_fence_is_xe_preempt()`. The fence ops provide driver/timeline names and `preempt_fence_enable_signaling()`. `preempt_fence_work_func()` performs asynchronous completion on the driver's ordered preempt fence workqueue.

## Control Flow and State

Allocation initializes the list link and work item. Unarmed fences can live on lists using the embedded link and must be freed with `xe_preempt_fence_free()`. Arming removes the link, stores a referenced exec queue, initializes the fence lock and `dma_fence`, and returns the embedded fence. Enabling signaling calls `q->ops->suspend(q)`, stores any immediate error, and queues work. The worker either sets the stored error, waits for suspend completion, retries on `-EAGAIN`, marks reset queues as `-ENOENT`, signals the fence, queues VM rebind work, and drops the exec queue reference.

## Dependencies and Integration Points

It depends on `dma_fence`, workqueues, exec queue operations, GuC exec queue IDs for debugging, GT logging, and VM rebind scheduling. It is part of the VM preempt-fence mode and rebind worker pipeline.

## Risks and Test Signals

The ordered global workqueue means blocking work in the callback can block all preempt fences; the code uses `dma_fence_begin_signalling()` to make lockdep catch unsafe locks. Retry loops rely on `suspend_wait()` eventually stopping returning `-EAGAIN`. Tests should cover allocation failure, unarmed free, arm lifetime, suspend success, immediate suspend error, reset-status error, retry behavior, queue reference release, VM rebind enqueue, and `xe_fence_is_xe_preempt()` distinguishing fence ops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_preempt_fence.c -->
