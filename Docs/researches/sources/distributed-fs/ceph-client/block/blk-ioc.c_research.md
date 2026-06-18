# sources/distributed-fs/ceph-client/block/blk-ioc.c

## Purpose
`blk-ioc.c` manages per-task `io_context` objects and, when `CONFIG_BLK_ICQ` is enabled, per-queue `io_cq` associations used by I/O schedulers. It handles reference counting, task inheritance, ioprio storage, scheduler callback lifetime, and queue cleanup.

## Important APIs, Types, and Functions
Important functions include `put_io_context()`, `exit_io_context()`, `set_task_ioprio()`, `__copy_io()`, `ioc_lookup_icq()`, `ioc_find_get_icq()`, and `ioc_clear_queue()`. Internal helpers include `alloc_io_context()`, `get_io_context()`, `ioc_exit_icq()`, `ioc_destroy_icq()`, `ioc_release_fn()`, `ioc_delay_free()`, and `ioc_create_icq()`.

## Control Flow
An `io_context` is allocated lazily when ioprio is set, a task copies I/O state, or an ICQ is requested. `set_task_ioprio()` checks credentials and LSM policy, allocates if needed, handles races with task exit or another allocator, and updates `ioc->ioprio`. `__copy_io()` shares the parent's context for `CLONE_IO`, otherwise copies only valid ioprio into a new context.

With `CONFIG_BLK_ICQ`, schedulers request a queue-specific context through `ioc_find_get_icq()`. It ensures a current task context exists, looks up an existing ICQ via RCU hint or radix tree, and creates one under both queue and ioc locks if missing. Queue clearing walks `q->icq_list` and destroys every association. Final ioc release is delayed to `system_power_efficient_wq` if ICQs remain, because destroying them requires queue/ioc double locking that might conflict with current lock context.

## State and Persistence
State is per-task `task->io_context`, `io_context.refcount`, `active_ref`, `ioprio`, optional radix tree/list of ICQs, RCU hint pointer, and per-queue `q->icq_list`. ICQs carry scheduler-specific storage allocated from the elevator's cache. No persistent state exists beyond task lifetime.

## Dependencies and Integration Points
This file integrates with task credentials, LSM `security_task_setioprio()`, sched/task exit, blk-mq schedulers, elevator ICQ callbacks, radix trees, RCU, queue locks, and slab cache initialization.

## Risks
Risks are lifetime and lock-order bugs between task exit, queue teardown, scheduler ICQ callbacks, and RCU lookup. The release worker performs careful double-locking and RCU protection to avoid freeing queues or ICQs while resolving lock order. Missing `put_io_context()` after `ioc_find_get_icq()` users would leak contexts.

## Test Signals
Tests should cover ioprio permission denial, LSM denial, lazy allocation races, `CLONE_IO` sharing, non-shared ioprio copy, ICQ lookup hint hits/misses, duplicate ICQ creation races, queue clearing during task exit, delayed release path, and builds without `CONFIG_BLK_ICQ`.
