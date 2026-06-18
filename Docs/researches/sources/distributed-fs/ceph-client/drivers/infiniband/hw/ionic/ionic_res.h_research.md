# sources/distributed-fs/ceph-client/drivers/infiniband/hw/ionic/ionic_res.h

Purpose: resource ID allocation helpers for Ionic RDMA and mapping helpers for UDMA-aware queue IDs. It wraps Linux IDA allocation and defines transforms between compact bit IDs and firmware queue IDs.

Important APIs/types: `struct ionic_resid_bits` owns an `ida` and size limit. Inline helpers are `ionic_resid_init()`, `ionic_resid_destroy()`, `ionic_resid_get_shared()`, `ionic_resid_get()`, `ionic_resid_put()`, `ionic_bitid_to_qid()`, and `ionic_qid_to_bitid()`.

Control flow: resource users initialize an allocator with a capacity, allocate IDs either across the full range or a caller-specified shared range, free IDs on object destruction, and destroy the IDA at device teardown. Queue ID helpers rearrange the UDMA bit and queue group bits so allocation can scan UDMA-specific halves while firmware sees queue IDs in group order.

State and persistence: ID allocation state is held by the IDA in `struct ionic_resid_bits` for the RDMA device lifetime. Queue ID mapping is stateless bit manipulation based on `qgrp_shift` and `half_qid_shift` from LIF configuration.

Dependencies and integration: depends on Linux IDA/IDR and bit helpers. `struct ionic_ibdev` owns allocators for doorbell IDs, PDs, AHs, MRs, QPs, and CQs; QID transforms are used for CQ/QP allocation across UDMA queue groups.

Risks: `ionic_resid_put()` trusts the ID is currently allocated. Queue transforms assume valid shifts and queue counts that are powers of two in the expected layout. Incorrect `half_qid_shift` or `qgrp_shift` can allocate queues on the wrong UDMA and break CQ/QP affinity.

Test signals: ID exhaustion/reuse, shared-range allocation boundaries, destroy with no leaks, round-trip `qid -> bitid -> qid` for all supported queue IDs, and UDMA-balanced QP/CQ allocation under load.
