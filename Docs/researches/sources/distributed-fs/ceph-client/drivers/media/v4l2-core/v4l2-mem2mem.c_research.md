# sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-mem2mem.c

## Purpose
`v4l2-mem2mem.c` implements the V4L2 memory-to-memory framework for drivers that process OUTPUT buffers into CAPTURE buffers through videobuf2. It provides context scheduling, ready-buffer queues, ioctl and file-operation helpers, request API queueing, draining semantics, and optional media-controller topology registration.

## Important APIs, Types, And Functions
The central private type is `struct v4l2_m2m_dev`, which stores current context, job queue, spinlock, work item, operation callbacks, kref, and optional media entities. Public helpers include queue accessors, ready-buffer operations, `v4l2_m2m_try_schedule()`, `v4l2_m2m_job_finish()`, `v4l2_m2m_buf_done_and_job_finish()`, suspend/resume, vb2 ioctl wrappers, mmap/poll helpers, encoder/decoder command helpers, `v4l2_m2m_init()`, `v4l2_m2m_ctx_init()`, `v4l2_m2m_ctx_release()`, `v4l2_m2m_buf_queue()`, and metadata/request helpers.

## Control Flow
Drivers initialize a device with `v4l2_m2m_init()` and a per-file context with `v4l2_m2m_ctx_init()`. Buffer queue callbacks add vb2 buffers to per-queue ready lists. `v4l2_m2m_try_schedule()` verifies streaming state, abort flags, source/destination availability, held capture timestamp rules, stopped state, and optional `job_ready()`, then queues one job per context. `v4l2_m2m_try_run()` selects the first queued context if no job is active and invokes driver `device_run()`. Completion removes the context from the job queue, wakes waiters, clears current context, and schedules the next run through workqueue context.

## State And Persistence
State lives in `struct v4l2_m2m_ctx` and queue contexts: ready lists, ready counts, streaming/draining/stopped flags, last source buffer, next-last capture marker, `new_frame`, and job flags `TRANS_QUEUED`, `TRANS_RUNNING`, and `TRANS_ABORT`. Device-wide state tracks `curr_ctx`, `job_queue`, paused state, media entities, and kref lifetime. Spinlocks protect ready lists and job state; optional queue mutexes protect file-operation paths.

## Dependencies And Integration Points
The framework integrates with videobuf2, V4L2 file handles/events, media requests, video device ioctls, media-controller entities, and driver callbacks in `struct v4l2_m2m_ops`. CAPTURE MMAP offsets are shifted by `DST_QUEUE_OFF_BASE` to distinguish the two queues. Optional media-controller registration creates source, processing, sink, and interface entities with immutable enabled links.

## Risks And Test Signals
Key risks are races between streamoff, job completion, request queueing, held capture buffers, and draining LAST-buffer handling. Tests should cover dual-queue streamon/order variations, nonblocking poll results, CAPTURE request rejection, MMAP offset adjustment for single and multiplanar buffers, streamoff during running and queued jobs, suspend waiting for current completion, encoder/decoder STOP/START state, stateless decoder FLUSH releasing held buffers, media-controller registration rollback, and kref release behavior.
# sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-mem2mem.c

## Purpose
`v4l2-mem2mem.c` implements the V4L2 memory-to-memory framework for drivers that process OUTPUT buffers into CAPTURE buffers through videobuf2. It provides context scheduling, ready-buffer queues, ioctl and file-operation helpers, request API queueing, draining semantics, and optional media-controller topology registration.

## Important APIs, Types, And Functions
The central private type is `struct v4l2_m2m_dev`, which stores current context, job queue, spinlock, work item, operation callbacks, kref, and optional media entities. Public helpers include queue accessors, ready-buffer operations, `v4l2_m2m_try_schedule()`, `v4l2_m2m_job_finish()`, `v4l2_m2m_buf_done_and_job_finish()`, suspend/resume, vb2 ioctl wrappers, mmap/poll helpers, encoder/decoder command helpers, `v4l2_m2m_init()`, `v4l2_m2m_ctx_init()`, `v4l2_m2m_ctx_release()`, `v4l2_m2m_buf_queue()`, and metadata/request helpers.

## Control Flow
Drivers initialize a device with `v4l2_m2m_init()` and a per-file context with `v4l2_m2m_ctx_init()`. Buffer queue callbacks add vb2 buffers to per-queue ready lists. `v4l2_m2m_try_schedule()` verifies streaming state, abort flags, source/destination availability, held capture timestamp rules, stopped state, and optional `job_ready()`, then queues one job per context. `v4l2_m2m_try_run()` selects the first queued context if no job is active and invokes driver `device_run()`. Completion removes the context from the job queue, wakes waiters, clears current context, and schedules the next run through workqueue context.

## State And Persistence
State lives in `struct v4l2_m2m_ctx` and queue contexts: ready lists, ready counts, streaming/draining/stopped flags, last source buffer, next-last capture marker, `new_frame`, and job flags `TRANS_QUEUED`, `TRANS_RUNNING`, and `TRANS_ABORT`. Device-wide state tracks `curr_ctx`, `job_queue`, paused state, media entities, and kref lifetime. Spinlocks protect ready lists and job state; optional queue mutexes protect file-operation paths.

## Dependencies And Integration Points
The framework integrates with videobuf2, V4L2 file handles/events, media requests, video device ioctls, media-controller entities, and driver callbacks in `struct v4l2_m2m_ops`. CAPTURE MMAP offsets are shifted by `DST_QUEUE_OFF_BASE` to distinguish the two queues. Optional media-controller registration creates source, processing, sink, and interface entities with immutable enabled links.

## Risks And Test Signals
Key risks are races between streamoff, job completion, request queueing, held capture buffers, and draining LAST-buffer handling. Tests should cover dual-queue streamon/order variations, nonblocking poll results, CAPTURE request rejection, MMAP offset adjustment for single and multiplanar buffers, streamoff during running and queued jobs, suspend waiting for current completion, encoder/decoder STOP/START state, stateless decoder FLUSH releasing held buffers, media-controller registration rollback, and kref release behavior.
