# sources/distributed-fs/ceph-client/drivers/infiniband/hw/ionic/ionic_queue.h

Purpose: ring-buffer abstraction for Ionic RDMA driver/device queues. It defines queue geometry, doorbell constants, allocation prototypes, and inline helpers for queue occupancy, indexing, wrap/color tracking, and doorbell values.

Important APIs/types: `struct ionic_queue` stores coherent memory, DMA address, producer/consumer indices, ring mask, depth/stride logs, and doorbell bits. Helpers include `ionic_queue_empty()`, `ionic_queue_length()`, `ionic_queue_length_remaining()`, `ionic_queue_full()`, `ionic_color_wrap()`, `ionic_queue_at()`, `ionic_queue_at_prod()`, `ionic_queue_at_cons()`, `ionic_queue_next()`, producer/consumer increment helpers, `ionic_queue_dbell_init()`, and `ionic_queue_dbell_val()`.

Control flow: queue users initialize memory with `ionic_queue_init()`, prepare entries at `prod` or inspect entries at `cons`, advance indices with mask arithmetic, and ring doorbells using the qid-initialized doorbell value ORed with the producer index. CQ polling uses `ionic_color_wrap()` to track device-owned CQE wrap state.

State and persistence: queue state lives entirely in `struct ionic_queue`. Producer and consumer semantics are direction-specific; comments note several helpers are valid only for to-device queues. Doorbell state persists as a precomputed qid field plus current producer bits.

Dependencies and integration: includes MMIO and Ionic register macros for doorbells. Used by admin queues, event queues, CQs, SQs, RQs, and datapath completion logic.

Risks: helpers do not bounds-check entry indices or enforce full/empty preconditions. Pointer arithmetic on `void *` is a GNU C kernel extension. Misusing to-device helpers on from-device queues can corrupt CQ interpretation. Color wrap assumes producer advances exactly as CQEs are consumed.

Test signals: producer/consumer wrap tests, queue-full and queue-empty behavior at mask boundaries, doorbell values for expected QIDs, CQ color toggling across wrap, and static analysis for callers holding required locks.
