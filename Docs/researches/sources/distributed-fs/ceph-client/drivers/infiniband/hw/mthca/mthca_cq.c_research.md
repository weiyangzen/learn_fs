# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_cq.c

## Purpose
`mthca_cq.c` implements completion queue allocation, arming, polling, CQE decoding, resize handoff, QP completion cleanup, and CQ event delivery for mthca.

## Important APIs, types, and functions
Important layouts are `struct mthca_cq_context`, `struct mthca_cqe`, and `struct mthca_err_cqe`. Public APIs include `mthca_init_cq()`, `mthca_free_cq()`, `mthca_poll_cq()`, `mthca_tavor_arm_cq()`, `mthca_arbel_arm_cq()`, `mthca_cq_completion()`, `mthca_cq_event()`, `mthca_cq_clean()`, `mthca_cq_resize_copy_cqes()`, `mthca_alloc_cq_buf()`, `mthca_free_cq_buf()`, and table init/cleanup. Internal helpers read CQEs from direct or page-list buffers, test ownership, update consumer indexes, and translate error syndromes.

## Control flow
CQ creation allocates a CQN, maps mem-free ICM and doorbell records when needed, allocates kernel CQ buffers, fills a CQ context, issues `SW2HW_CQ`, publishes the CQ in the lookup array, and initializes the consumer index. Completion events increment arm sequence and invoke the RDMA CQ completion handler. Polling repeatedly consumes software-owned CQEs, locates the QP, derives WR IDs from SQ/RQ/SRQ state, updates WQ tails, translates success or error CQEs into `ib_wc`, returns ownership to hardware, and writes consumer index updates. Freeing transitions the CQ back to software, removes it from the table, synchronizes IRQs, waits for event refs, and releases buffers, DBs, ICM refs, and CQN.

## State and persistence
State includes CQ number, CQ buffer/MR, consumer index, arm sequence, resize buffer state, refcount/waitqueue, kernel/user ownership, doorbell records, and table array entries. Hardware persists CQ context, producer state, CQE ownership bits, and notification state.

## Dependencies and integration points
It depends on command wrappers, allocator/buffer MR helpers, memfree table/doorbell helpers, QP and SRQ tables, RDMA CQ handlers, EQ completion/error events, and architecture MMIO/barrier helpers.

## Risks
CQ polling is concurrency-sensitive. QP lookup assumes QP removal locks CQs. Error CQE handling for Tavor may rewrite CQEs instead of freeing them. Resize swaps buffers only after the old buffer appears empty. Refcounting must prevent event callbacks from racing CQ free. Consumer-index updates differ between Tavor doorbells and Arbel doorbell records, making barriers critical.

## Test signals
Test kernel/user CQ create/free, mem-free and Tavor modes, CQ polling for send/recv/RDMA/atomic/immediate completions, every error syndrome mapping, SRQ receive completions and cleanup, CQ overrun/access-violation async events, arm solicited/all modes, resize while completions exist, QP reset cleanup, IRQ synchronization during free, and KASAN/lockdep stress.
