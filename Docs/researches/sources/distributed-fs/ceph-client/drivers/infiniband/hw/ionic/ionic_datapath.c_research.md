# sources/distributed-fs/ceph-client/drivers/infiniband/hw/ionic/ionic_datapath.c

Purpose: Ionic RoCE datapath verbs implementation. It posts send and receive work requests, prepares firmware WQEs, polls completion queues, translates device completion status into `ib_wc`, handles CQ notification arming, and drains flushed QPs after error or destroy transitions.

Important APIs/functions: exported verbs hooks are `ionic_post_send()`, `ionic_post_recv()`, `ionic_poll_cq()`, and `ionic_req_notify_cq()`. Internal helpers include `ionic_next_cqe()`, `ionic_poll_recv()`, `ionic_poll_send()`, `ionic_comp_msn()`, `ionic_comp_npg()`, `ionic_flush_send_many()`, `ionic_flush_recv_many()`, WQE preparation helpers for send, UD send, RDMA, atomic, local invalidate, fast register MR, and receive posting.

Control flow: CQ polling alternates across per-UDMA CQs in a `struct ionic_vcq`, first emits send completions already made visible by earlier CQEs, then consumes device CQEs while color matches, then drains flush lists. Receive CQEs validate QP lookup, queue state, WQE ID, and posted metadata before filling `ib_wc`. Send completions are split between MSN completions for remote progression and NPG completions for local progression; `ionic_poll_send()` emits only signaled or error completions. Posting validates QP state and queue capacity, prepares WQEs by opcode, advances producer indices, reserves CQ credits, and rings SQ/RQ doorbells.

State and persistence: state is in `struct ionic_qp` queue producers/consumers, SQ metadata, RQ free-list metadata, MSN sequence arrays, flush flags, and CQ lists. `struct ionic_cq` tracks color, credit, arm producer counters, and pending poll/flush lists. The file does not persist to disk; hardware-visible state is coherent queue memory and doorbell writes.

Dependencies and integration: depends on `ionic_fw.h` ABI layouts/opcodes, `ionic_queue.h` ring helpers, `ionic_ibdev.h` object containers, RDMA core work request/completion structures, xarray QP lookup, DMA barriers, and Ionic doorbell registers from the Ethernet device integration.

Risks: queue ownership relies on color bits, producer/consumer arithmetic, and CQ credit accounting. Error CQEs move QPs to flush lists, so missed list transitions can stall completions. `ionic_prep_atomic()` calls `ionic_prep_common()` after filling the atomic body, which reuses common SGL preparation and must remain layout-compatible. Inline posting copies from user-provided virtual addresses already accepted by RDMA core, so opcode and size validation are the main guardrails. Several invalid device completion cases return `-EIO` after warnings.

Test signals: RDMA send/recv, RDMA read/write, immediate data, invalidation, atomics, fast-reg MR, UD/GSI receive metadata, CQ arming with `IB_CQ_REPORT_MISSED_EVENTS`, queue-full posting, signaled versus unsignaled sends, and QP error flush behavior.
