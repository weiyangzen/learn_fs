# sources/distributed-fs/ceph-client/drivers/infiniband/hw/bnxt_re/qplib_fp.c

## Purpose
`qplib_fp.c` implements the qplib fast path for notification queues, shared receive queues, queue pairs, completion queues, posting send/receive work requests, processing CQEs, and fabricating flush completions when QPs enter error. It is the main bridge between RDMA verbs objects created by `ib_verbs.c`, firmware RCFW commands, hardware queue memory, doorbells, and completion delivery.

## Important APIs, types, and functions
Public entry points include `bnxt_qplib_alloc_nq()`, `bnxt_qplib_enable_nq()`, `bnxt_qplib_create_srq()`, `bnxt_qplib_post_srq_recv()`, `bnxt_qplib_create_qp1()`, `bnxt_qplib_create_qp()`, `bnxt_qplib_modify_qp()`, `bnxt_qplib_query_qp()`, `bnxt_qplib_destroy_qp()`, `bnxt_qplib_post_send()`, `bnxt_qplib_post_recv()`, `bnxt_qplib_create_cq()`, `bnxt_qplib_resize_cq()`, `bnxt_qplib_destroy_cq()`, `bnxt_qplib_poll_cq()`, and `bnxt_qplib_req_notify_cq()`. Important internal helpers manage QP1 header DMA buffers, PSN/MSN search entries, variable WQE slot accounting, CQ/NQ tasklets, flush lists, SRQ free lists, and the WA9060 phantom/fence workaround.

## Control flow
NQs are allocated as qplib HWQs, mapped to BAR doorbells, armed, and serviced by MSI-X IRQs that schedule tasklets. NQ tasklets decode CQ notification and SRQ event entries, rearm device queues, update user toggle pages, and call upper callbacks. QP/CQ/SRQ creation allocates queue memory, sends RCFW create commands, stores firmware IDs, initializes doorbell metadata, and sets up software queue rings. Post-send/post-recv validate state and space, fill WQE headers and SGEs or inline payload, update PSNs/search tables, advance software and hardware producers, and leave actual doorbell ringing to the caller-specific DB helpers. CQ polling validates CQE toggles, decodes request/response/terminal/cutoff formats, advances queue consumers, marks error QPs, and rings CQ consumer doorbells.

## State and persistence
Fast-path state lives in `bnxt_qplib_qp`, `bnxt_qplib_q`, `bnxt_qplib_swq`, `bnxt_qplib_cq`, `bnxt_qplib_srq`, and `bnxt_qplib_nq`. The driver tracks producer/consumer indices, toggle bits, flush-list membership, PSN/MSN metadata, per-WR IDs, DMA header buffers, CQ arm state, and NQ workqueues. Firmware persists QP/CQ/SRQ/NQ object IDs and queue context. User queue memory is represented by umem-backed HWQs; kernel queues are coherent DMA pages.

## Dependencies and integration points
The file depends on `roce_hsi.h` hardware descriptors, qplib resource allocation, RCFW send-message commands, qplib doorbell helpers from resource headers, Linux IRQ/tasklet/workqueue APIs, RDMA MAD/QP1 handling, and upper bnxt_re wrappers for CQ/SRQ/QP container conversion. It is called heavily from `ib_verbs.c`.

## Risks
This code is concurrency-sensitive. Flush lists require CQ flush locks and upper CQ locks to avoid races with poll and async QP errors. `bnxt_qplib_process_flush_list()` uses `list_for_each_entry()` while flush helpers can empty queues but do not remove QPs from lists, so repeated polling depends on flushed flags and external cleanup. Posting to an ERR QP schedules CQ work using `GFP_ATOMIC`; allocation failure changes error reporting. Variable WQE error recovery searches `swq` by slot and can skip completions if firmware reports unexpected slot indices. The source snapshot has duplicated `single` and duplicated `srqn_handler_t` lines in the header. Several CQ paths trust firmware-provided handles and indices before validating all bounds.

## Test signals
Cover kernel and user QP create/destroy, QP1 header buffers, SRQ post/release, static and variable WQE modes, inline send length limits, RDMA read/write, atomics, fast-reg MR, bind MW, zero-SGE receive, CQ resize cutoff completion, CQ arm/rearm, NQ IRQ restart, QP error async flush, terminal CQEs, SRQ events, and firmware malformed CQE indices. KASAN/KCSAN/lockdep are useful because most defects would be lifetime or locking issues.
