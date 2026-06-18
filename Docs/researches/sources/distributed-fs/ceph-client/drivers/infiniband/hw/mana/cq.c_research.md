# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mana/cq.c

## Purpose
`cq.c` creates, destroys, arms, services, and polls MANA completion queues, including a kernel shadow-completion path for UD/GSI work requests.

## Important APIs, Types, And Functions
`mana_ib_create_cq()` creates user or kernel CQs, validates CQE limits, creates a queue, optionally creates an RNIC CQ via `mana_ib_gd_create_cq()`, installs a GDMA callback, and returns the CQ ID to userspace. `mana_ib_destroy_cq()` removes the callback, destroys the RNIC CQ, and frees queue resources. `mana_ib_install_cq_cb()` and `mana_ib_remove_cq_cb()` manage `gdma_context->cq_table`. `mana_ib_arm_cq()` rings a kernel CQ arm doorbell. `mana_ib_poll_cq()` polls GDMA completions, calls `mana_handle_cqe()`, and then converts shadow WQEs into `ib_wc` entries.

## Control Flow
Creation branches on `udata`: user CQs pin userspace memory and use the ucontext doorbell; kernel CQs allocate a GDMA queue and use the device doorbell. For RNIC devices, a firmware CQ object and callback entry are installed before optional udata response. Completion callbacks invoke the RDMA CQ handler. Polling holds `cq_lock`, drains up to `num_entries` hardware CQEs, uses queue ID and SQ/RQ bit to find the QP, advances UD shadow queues, then emits completions from send and receive shadow queues.

## State And Persistence
`struct mana_ib_cq` stores queue metadata, a spinlock, lists of send/recv QPs attached to the CQ, CQE count, completion vector, and firmware CQ handle. Callback state is in `gdma_context->cq_table`. Completion state for UD/GSI is stored in per-QP shadow queues, not in the CQ itself. All state is runtime-only.

## Dependencies And Integration Points
The file integrates RDMA core CQ ops, MANA GDMA queue APIs, firmware CQ commands in `main.c`, QP lookup/refcount helpers in `mana_ib.h`, UD shadow queues in `shadow_queue.h`, and QP list management in `qp.c`.

## Risks
`mana_ib_arm_cq()` only supports kernel CQs because user CQs have no `queue.kmem`; callers must not arm unsupported CQs. `mana_ib_remove_cq_cb()` returns early for kernel queues and relies on the MANA core to clean callback table entries, so lifetime coupling is subtle. Shadow queues silently drop hardware completions when `shadow_queue_get_next_to_complete()` returns NULL. Polling assumes `cq->queue.kmem` is valid, which is not true for user CQs in the RNIC path unless userspace polling bypasses this kernel function.

## Test Signals
Test user and kernel CQ creation, RNIC and non-RNIC modes, max CQE validation, callback table collision, udata copy failure unwind, arm on kernel versus user CQs, UD/GSI send and receive completions, shadow-queue empty/full edge cases, CQ destroy with active QPs, and GDMA CQ polling errors or empty polls.
