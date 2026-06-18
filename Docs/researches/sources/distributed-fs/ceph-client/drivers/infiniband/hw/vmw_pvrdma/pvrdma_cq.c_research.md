<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/vmw_pvrdma/pvrdma_cq.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/vmw_pvrdma/pvrdma_cq.c

## Purpose

Implements PVRDMA completion queue creation, destruction, notification arming, CQE flushing, and polling.

## Important APIs, Types, And Functions

Public handlers are `pvrdma_create_cq()`, `pvrdma_destroy_cq()`, `pvrdma_req_notify_cq()`, `pvrdma_poll_cq()`, and `_pvrdma_flush_cqe()`. Helpers include `pvrdma_free_cq()`, `get_cqe()`, and `pvrdma_poll_one()`.

## Control Flow

Create validates flags and CQE count, reserves a device CQ counter, handles user CQs through `ib_umem_get()` or kernel CQs through driver-allocated page directories, posts `PVRDMA_CMD_CREATE_CQ`, stores the returned handle in `dev->cq_tbl`, and returns a CQ number to userspace. Notify writes the CQ handle plus arm bits to the UAR and can report missed events by checking the ring. Poll reads the kernel CQ ring, asks the device to poll once on an empty ring, translates CQEs to `ib_wc`, and advances the consumer head.

Destroy posts `PVRDMA_CMD_DESTROY_CQ`, clears the table entry, waits for event-handler references to drain through `refcnt` and `free`, releases umem/page-directory resources, and decrements counters.

## State And Persistence Behavior

Each CQ keeps a page directory, optional user umem, ring state, CQ handle, kernel/user flag, spinlock, refcount, and completion. Device-level state includes `num_cqs` and `cq_tbl`. CQEs persist in shared ring memory until consumed or flushed.

## Dependencies And Integration Points

Integrates with RDMA core CQ ops, userspace ABI structs, PVRDMA command ABI, page-directory helpers, UAR doorbells, QP table lookups for completions, and async/completion interrupts in `pvrdma_main.c`.

## Risks And Edge Cases

`pvrdma_destroy_cq()` clears `dev->cq_tbl[vcq->cq_handle]` while create indexes by `handle % max_cq`; this is safe only if handles are bounded as table indexes. `_pvrdma_flush_cqe()` only handles kernel CQs and rewrites ring contents; off-by-one errors here would drop or duplicate completions during QP reset/destroy. User CQ ring state is trusted to userspace-provided memory layout but pinned through umem.

## Test Signals

Tests should cover user and kernel CQ creation, max CQ/CQE limits, missed-event reporting, solicited/all notification arming, polling empty and non-empty rings, QP destroy flushing, CQ event refcounting, and destroy after failed userspace copyback.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/vmw_pvrdma/pvrdma_cq.c -->
