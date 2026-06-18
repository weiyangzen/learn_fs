<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/cq.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/cq.c

## Purpose

Implements software completion queues for rdmavt, including creation, mmap-backed userspace queues, completion insertion, notification delivery, resize, poll, and workqueue lifecycle.

## Important APIs, Types, And Functions

Public handlers are `rvt_cq_enter()`, `rvt_create_cq()`, `rvt_destroy_cq()`, `rvt_req_notify_cq()`, `rvt_resize_cq()`, `rvt_poll_cq()`, `rvt_driver_cq_init()`, and `rvt_cq_exit()`. `send_complete()` runs completion callbacks from a per-CPU high-priority workqueue.

## Control Flow

Create validates flags and size, allocates a user `rvt_cq_wc` through `vmalloc_user()` when userspace expects an mmap offset or a kernel `rvt_k_cq_wc` through `vzalloc_node()`, creates mmap info for user queues, reserves a CQ count, sets CPU affinity for the completion vector, and initializes locks/work. `rvt_cq_enter()` writes a completion to the user or kernel ring, validates user-writable head, detects full queues, fires CQ error events, and queues completion work when notification rules match. Poll drains kernel queues. Resize allocates a new ring, validates the existing user-modifiable head/tail, copies pending entries, swaps queues, and updates mmap info for userspace.

## State And Persistence Behavior

CQ state includes ring buffers, head/tail counters, notification mode, full flag, pending mmap info, completion work, selected CPU, and device CQ allocation count. User queues persist as vmalloc memory mapped through `rvt_mmap()` and reference-counted by mmap info.

## Dependencies And Integration Points

Depends on RDMA core CQ APIs, rdmavt mmap helpers, tracepoints, workqueues, vmalloc, uverbs copyout, and optional driver completion-vector CPU lookup.

## Risks And Edge Cases

User queues expose head/tail fields to userspace, so every path must sanitize them. Full CQ handling sets a sticky `cq_full` and reports `IB_EVENT_CQ_ERR`. Completion callbacks are serialized through workqueue semantics but `triggered` is used to catch events queued during callback execution. Resize must not shrink below pending completion count.

## Test Signals

Test kernel/user CQ creation, max limits, mmap offset return, CQ full behavior and event delivery, notification transitions and missed-event reporting, poll order, resize with wrapped head/tail, invalid user head/tail values, destroy flushing pending work, and workqueue init/exit.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/cq.c -->
