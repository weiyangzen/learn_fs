# File Research: sources/block-storage/kvdo/vdo/workQueue.h

## Purpose
Declares the VDO work-queue API and queue-type descriptor used by the completion-processing subsystem.

## Public Types
- `MAX_VDO_WORK_QUEUE_NAME_LEN`: aliases `TASK_COMM_LEN`.
- `struct vdo_work_queue_type`: optional start/finish hooks plus max/default completion priority.

## Public API
- `make_work_queue()`: creates a simple or round-robin work queue.
- `enqueue_work_queue()`: submits a `vdo_completion`.
- `finish_work_queue()`: stops worker threads.
- `free_work_queue()`: finishes and frees the queue.
- `dump_work_queue()`: logs queue state.
- `dump_completion_to_buffer()`: writes compact completion debug info.
- `get_work_queue_private_data()`: returns current queue private data.
- `get_current_work_queue()`: returns the queue for the current worker thread.
- `get_work_queue_owner()`: returns the owning `vdo_thread`.
- `vdo_work_queue_type_is()`: checks queue type identity.

## Dependencies
Includes Linux `<linux/sched.h>` for `TASK_COMM_LEN`, plus `funnel-queue.h`, `kernel-types.h`, and `types.h`.

## Notes
The header exposes `struct vdo_work_queue` opaquely. Implementation details are private to `workQueue.c`.
