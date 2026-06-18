# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/funnel-workqueue.h

## Purpose
`funnel-workqueue.h` declares the public VDO workqueue API and the workqueue type descriptor used by completion scheduling code.

## Important APIs, Types, And Functions
- `MAX_VDO_WORK_QUEUE_NAME_LEN` ties queue names to Linux `TASK_COMM_LEN`.
- `struct vdo_work_queue_type` defines optional `start` and `finish` hooks plus `max_priority` and `default_priority`.
- Opaque types include `struct vdo_completion`, `struct vdo_thread`, and `struct vdo_work_queue`.
- Public APIs create, enqueue, finish, free, dump, inspect current queue/private data/owner, and compare queue type.

## Control Flow And Data Flow
Callers define a queue type, create a queue with one or more worker threads, enqueue initialized `vdo_completion` objects, and finish/free the queue during teardown. The default priority is applied when a completion uses `VDO_WORK_Q_DEFAULT_PRIORITY`.

## State And Persistence Behavior
The header exposes no persistent state. It defines the contracts for transient completion execution and thread-private context attached to worker queues.

## Dependencies And Integration Points
It depends on Linux scheduling constants and VDO `types.h`. It is consumed by VDO completion infrastructure and modules that create named execution domains.

## Risks
- Queue type priority bounds must not exceed the implementation's `VDO_WORK_Q_MAX_PRIORITY`.
- Caller-provided private contexts must outlive the worker thread that uses them.
- The API does not by itself prevent enqueue-after-finish; lifecycle ordering is external.

## Test Signals
Compile-time coverage should confirm all completion users include this interface cleanly. Runtime tests should validate that type matching, owner lookup, and private-data lookup behave correctly from worker and non-worker contexts.
