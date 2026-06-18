<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/cq.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/core/cq.c

## Purpose

`cq.c` implements kernel RDMA completion queue allocation, polling, notification, shared CQ pooling, and optional RDMA DIM interrupt moderation. It provides higher-level CQ helpers for in-kernel users that process `wr_cqe` callbacks in direct, softirq, bound workqueue, or unbound workqueue contexts.

## Important APIs, types, and functions

Exported entry points are `ib_process_cq_direct()`, `__ib_alloc_cq()`, `__ib_alloc_cq_any()`, `ib_free_cq()`, `ib_cq_pool_get()`, and `ib_cq_pool_put()`. `ib_cq_pool_cleanup()` is declared in `core_priv.h` for device teardown.

Important helpers are `__poll_cq()`, `__ib_process_cq()`, `ib_poll_handler()`, `ib_cq_completion_softirq()`, `ib_cq_poll_work()`, `ib_cq_completion_workqueue()`, `ib_cq_completion_direct()`, `rdma_dim_init()`, `rdma_dim_destroy()`, `ib_cq_rdma_dim_work()`, and `ib_alloc_cqs()`. The file uses `struct ib_cq`, `struct ib_wc`, `struct ib_cqe`, `struct irq_poll`, `struct dim`, device CQ ops, trace events from `rdma_core`, and global RDMA completion workqueues.

## Control flow

`__ib_alloc_cq()` validates the requested CQE count, allocates a driver CQ object and polling WC buffer, creates resource-tracker state, calls the driver `create_cq` op, optionally initializes DIM, then installs a completion handler based on polling context. Direct CQs warn on unsolicited completion and must be polled by the caller. Softirq CQs initialize `irq_poll`, request notification, and schedule polling from the completion handler. Workqueue CQs initialize work and queue polling on either `ib_comp_wq` or `ib_comp_unbound_wq`.

Polling uses `__ib_process_cq()` to call `ib_poll_cq()` in batches, invoke each `wr_cqe->done()` callback, count completions, and stop on budget or short poll. Softirq and workqueue pollers re-arm notifications with `IB_CQ_NEXT_COMP | IB_CQ_REPORT_MISSED_EVENTS`; if the device reports missed events or the workqueue budget is exhausted, they reschedule themselves. DIM samples completion counts and schedules `modify_cq` work to change moderation profile when enabled.

`ib_free_cq()` refuses to free CQs with users or pooled CQE reservations, runs optional pre-destroy, disables polling context, destroys DIM, calls driver post-destroy or destroy, removes restrack, and frees buffers. Shared CQ pooling finds a CQ with matching completion vector and enough unused CQEs, or allocates one CQ per vector/CPU into a per-device pool. `ib_cq_pool_put()` returns the reserved CQE count.

## State and persistence

State is runtime only. Each CQ tracks poll context, completion vector, WC batch buffer, optional DIM state, work/irq-poll objects, resource-tracker entry, use count, shared-pool flag, and `cqe_used` reservations for pooled CQs. Device-level state includes `cq_pools[]` and `cq_pools_lock`. There is no disk persistence; CQ state is destroyed on CQ free or device teardown.

## Dependencies and integration points

The file depends on RDMA verbs, device CQ ops (`create_cq`, `destroy_cq`, `pre_destroy_cq`, `post_destroy_cq`, `modify_cq`), resource tracking, Linux workqueues, irq_poll, DIM, online CPU counts, and RDMA core trace events. It integrates with kernel ULPs allocating CQs, verbs code that directly polls CQs, device cleanup through `ib_cq_pool_cleanup()`, and drivers that support CQ moderation.

## Risks

The main risks are concurrency and accounting. A CQ must not be freed while usecnt or pooled CQE reservations remain. Completion rearming must handle missed events or completions can stall. Direct polling on non-direct CQs can race with automatic polling. Workqueue budget rescheduling must avoid livelock while still draining busy CQs. Shared CQ allocation uses global/static vector counters and per-device pool locks; incorrect `cqe_used` accounting can overcommit or leak CQEs. DIM work must be canceled before CQ destruction and must not call `modify_cq` after the device object is gone.

## Test signals

Validation should allocate/free CQs in each poll context, post WRs with `wr_cqe` callbacks, verify direct polling drains completions, verify softirq/workqueue polling re-arms and handles missed events, stress shared pool get/put with vector hints and capacity limits, run device teardown with pooled CQs, enable DIM on capable devices and observe `modify_cq` calls, and check trace events for CQ allocation, polling, scheduling, rescheduling, modification, and free. WARNs on usecnt, `cqe_used`, unsolicited direct completions, or destroy failures indicate regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/cq.c -->
