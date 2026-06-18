# sources/distributed-fs/ceph-client/drivers/infiniband/sw/siw/siw_qp_tx.c

Purpose: Implements the transmit-side SoftiWARP SQ engine. It validates WQE memory, builds RDMAP/DDP/MPA headers, handles inline and fragmented payloads, computes optional MPA CRC, sends through kernel TCP sockets with copy or zero-copy page splicing, processes local REG_MR/LOCAL_INV operations, and schedules per-CPU TX worker execution.

Important APIs/types/functions: `siw_qp_prepare_tx()` builds one complete short FPDU or initializes fragmented send state. `siw_prepare_fpdu()` sizes each FPDU to TCP MSS/GSO limits and sets DDP LAST/padding. `siw_tx_ctrl()` sends complete control/header fragments. `siw_tx_hdt()` sends header-data-trailer FPDUs and updates partial-send state. `siw_0copy_tx()` and `siw_tcp_sendpages()` implement page-based TX. `siw_check_sgl_tx()` resolves SGEs. `siw_qp_sq_proc_tx()` processes wire operations; `siw_qp_sq_proc_local()` handles local memory verbs. `siw_qp_sq_process()`, `siw_sq_start()`, `siw_run_sq()`, `siw_create_tx_threads()`, and `siw_stop_tx_threads()` implement scheduling.

Control flow: Post-send or IRQ activation prepares a current WQE. If first processing, memory is checked, bytes are calculated, TCP segment length updated, and a short or fragmented FPDU is prepared. The TX loop sends control-only or HDT data, pauses on `-EAGAIN`, reschedules on burst exhaustion, completes successful WQEs, or drops the connection and completes errors on failure.

State and persistence behavior: TX state lives in `siw_iwarp_tx`: current packet union, sent header bytes, bytes unsent, WQE progress, SGE/PBL indices, CRC state, sendpage and GSO flags, ORQ fence flag, and syscall context. Per-CPU worker queues are in `llist_head`s. No persistent state.

Dependencies/integration: Uses TCP sendmsg/sendpage internals, page mapping, RDMA memory helpers, QP completion helpers, CM drop, CPU TX workers from `siw_main.c`, and `iwarp_pktinfo[]` templates.

Risks: Partial TCP sends must leave resumable state exactly correct, including CRC and trailer progress. Zero-copy with unsignalled user buffers has lifetime/immutability assumptions. ORQ cleanup on failed READ send is race-sensitive with loopback RRESP. Fragment array sizing and kmap ordering are correctness and safety risks.

Test signals: Short inline SEND/WRITE, multi-SGE large payloads, send pauses at header/data/trailer, CRC enabled, zero-copy threshold behavior, GSO/no-GSO, RDMA READ loopback, ORQ full, fenced WQEs, REG_MR/LOCAL_INV, TX CPU worker wakeup, CPU offline reassignment, and injected TCP send errors.
