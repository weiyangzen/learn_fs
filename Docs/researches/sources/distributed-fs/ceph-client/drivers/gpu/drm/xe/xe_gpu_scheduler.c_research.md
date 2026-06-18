<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gpu_scheduler.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gpu_scheduler.c

## Purpose
`xe_gpu_scheduler.c` wraps the DRM GPU scheduler with Xe-specific in-band message processing. It lets backends queue messages onto the scheduler submit workqueue while respecting scheduler stopped state.

## Important APIs, types, and functions
`xe_sched_init()` initializes the embedded DRM scheduler, Xe backend ops, message lock/list, and message work item. `xe_sched_fini()` stops submission and finalizes DRM scheduler state. `xe_sched_submission_start()`, `_stop()`, and `_resume_tdr()` control scheduler execution. `xe_sched_add_msg()`, `_locked()`, and `_head()` enqueue backend messages. Internal helpers process queued messages one at a time on `base.submit_wq`.

## Control flow and integration points
Adding a message takes `msg_lock`, appends or prepends the message, and queues processing if the scheduler is not stopped. Work exits immediately if stopped, otherwise removes the first message, calls `sched->ops->process_msg(msg)`, then schedules itself again if more messages remain. Start begins the DRM scheduler workqueue and queues message work; stop stops the scheduler queue and cancels message work synchronously.

## State and persistence behavior
`struct xe_gpu_scheduler` owns the DRM scheduler base, message list, spinlock, backend ops pointer, and work item. Message ownership is backend-defined; `process_msg` is responsible for freeing dynamically allocated messages.

## Dependencies, risks, and test signals
Dependencies include DRM GPU scheduler semantics, backend ops, workqueues, and Xe scheduler types. Risks include lost messages during stop/start, process_msg blocking submit work too long, callers using locked add without holding `msg_lock`, and message lifetime leaks. Test signals include GuC/backend message ordering, start/stop/resume TDR, stopped scheduler no-processing behavior, lockdep for locked add paths, and teardown with pending messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gpu_scheduler.c -->
