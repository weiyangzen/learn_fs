# sources/distributed-fs/ceph-client/drivers/infiniband/sw/siw/siw_qp.c

Purpose: Implements QP-level state transitions, socket data/write callbacks after connection establishment, read-queue initialization, terminate-message generation, SQ/RQ/ORQ/IRQ activation, completion production, queue flushing, and QP xarray lifetime.

Important APIs/types/functions: `iwarp_pktinfo[]` defines per-RDMAP opcode header templates and RX handlers. `siw_qp_llp_data_ready()` consumes TCP payload through `siw_tcp_rx_data()` when QP is RTS. `siw_qp_llp_close()` transitions QPs on LLP close and flushes queues. `siw_qp_mpa_rts()` creates MPAv2 zero-length RTR READ/WRITE work. `siw_qp_modify()` handles SIW state transitions and access flags. `siw_activate_tx()` selects between pending inbound read responses and SQ work. `siw_sqe_complete()` and `siw_rqe_complete()` write CQEs and fire CQ callbacks. `siw_sq_flush()` and `siw_rq_flush()` complete queued/in-progress work with flush errors. `siw_qp_add()` and `siw_free_qp()` manage xarray registration and teardown.

Control flow: CM/verbs call `siw_qp_modify()` to move IDLE/RTR into RTS once MPA succeeds. Post-send paths queue SQEs and call `siw_activate_tx()`, which may serve IRQ read responses before local SQ work. RX completion of read responses releases ORQ and may resume fenced TX. Close/error paths suspend RX/TX, send terminate when possible, drop CM, and flush queues.

State and persistence behavior: QP state is guarded by `state_lock`; SQ/RQ/ORQ have spinlocks or state-lock-only flush assumptions. Queue indices are free-running counters modulo power-of-two sizes. Completion state is shared with CQ rings and possibly userspace mmap. No persistence outside kernel objects.

Dependencies/integration: Integrates CM CEPs, TCP callbacks, TX/RX files, memory helpers, CQ events, and RDMA core events. Uses krefs and xarray for QP lookup.

Risks: State transitions and flushes are race-prone with socket callbacks, TX workers, and QP destruction. CQ overflow handling must not leave WQEs permanently valid. ORQ/IRQ fairness and fencing can deadlock if flags or indices are mishandled. Terminate generation reconstructs headers and is protocol-sensitive.

Test signals: QP state matrix, active/passive close, simultaneous socket close and destroy, SQ/RQ flush order, CQ overflow, fenced reads, ORQ full/resume, IRQ starvation prevention, remote terminate, and invalid work opcode/status paths.
