# sources/distributed-fs/ceph-client/drivers/infiniband/hw/cxgb4/qp.c

## Purpose

`qp.c` implements Chelsio iWARP queue pair and shared receive queue lifecycle, work request construction, posting, doorbell ringing, QP state transitions, RDMA init/fini/terminate firmware messages, drain completions, and error flushing. It is the main bridge between RDMA core verbs (`create_qp`, `post_send`, `modify_qp`, SRQ verbs) and T4/T5/T6 firmware work request formats.

## Important APIs, Types, and Functions

- Module parameters: `db_delay_usecs`, `ocqp_support`, `db_fc_threshold`, `db_coalescing_threshold`, and `max_fr_immd` tune doorbell and fast-registration behavior.
- Queue allocation: `alloc_sq`, `alloc_oc_sq`, `alloc_host_sq`, `create_qp`, `destroy_qp`, `alloc_srq_queue`, and `free_srq_queue`.
- Work request builders: `build_immd`, `build_isgl`, `build_rdma_send`, `build_rdma_write`, `build_rdma_read`, `build_memreg`, `build_tpte_memreg`, `build_inv_stag`, `build_rdma_recv`, and `build_srq_recv`.
- Fast path: `post_write_cmpl` coalesces a WRITE plus SEND/SEND_WITH_INV chain into one firmware `RDMA_WRITE_CMPL` WR for NVMe-oF-style responses.
- Posting APIs: `c4iw_post_send`, `c4iw_post_receive`, `c4iw_post_srq_recv`.
- QP state/control: `c4iw_modify_qp`, `c4iw_ib_modify_qp`, `rdma_init`, `rdma_fini`, `post_terminate`, `flush_qp`, and `__flush_qp`.
- SRQ support: `c4iw_create_srq`, `c4iw_destroy_srq`, `c4iw_modify_srq`, `c4iw_copy_wr_to_srq`, and deferred pending WR handling for out-of-order SRQ consumption.

## Control Flow

QP creation validates RC-only semantics, CQ handles, inline/WR limits, and optional SRQ use. It sizes SQ/RQ rings with an extra empty slot and status entries, allocates a firmware wait object, obtains QIDs/RQT memory, allocates host or on-chip SQ memory, allocates RQ memory when needed, resolves BAR2 doorbell addresses, and posts `FW_RI_RES_WR` resource commands. For userspace QPs it also returns queue IDs, sizes, flags, and mmap keys for SQ/RQ memory and doorbells.

Posting send WRs takes the QP spinlock, handles already-flushed QPs by generating software drain CQEs, checks SQ capacity, optionally takes the write-completion coalescing fast path, then builds one firmware WR per IB WR. It records a shadow `t4_swsqe`, initializes the firmware header, advances ring indices, and rings the SQ doorbell directly or through doorbell flow-control deferral. Receive posting mirrors this for RQ or SRQ rings and tracks wr_id metadata in software arrays.

QP modification is a mutex-protected state machine. IDLE can update RDMA attributes or transition to RTS via `rdma_init`. RTS can close, terminate, or error, sending FINI/TERMINATE and disconnecting the endpoint as needed. ERROR can return to IDLE only after SQ/RQ are empty. Error paths disassociate the endpoint, mark queues in error, flush CQs, and wake destroy waiters.

## State and Persistence Behavior

Persistent per-QP state includes hardware QIDs, DMA queue memory, BAR2 doorbell mapping, software SQ/RQ shadows, QP attributes, endpoint pointer/refcount, wait queues, and resource-tracking xarray membership. Firmware-visible state persists in Chelsio queue contexts and RI connection state until reset/fini/destroy commands complete. Doorbell state may be deferred in `db_fc_list` when the adapter status page reports doorbells off. SRQs maintain normal ring indices plus pending and out-of-order counters.

## Dependencies and Integration Points

The file depends on `t4.h` ring helpers and CQE macros, `t4fw_ri_api.h` firmware layouts, `resource.c` QID/RQT/OCQP allocation, CQ flush/count helpers, MR invalidation/access conversion, endpoint/CM code for LLP connection ownership, and RDMA core uverbs structures. It integrates with userspace through mmap entries prepared here and consumed by `provider.c`.

## Risks and Edge Cases

- The unwind path under `err_free_rq_db_key` has an unbraced duplicated `kfree(rq_db_key_mm)`, causing a double free when no SRQ is used.
- `build_rdma_read` sets dummy STAG 2 for zero-length reads; tests should confirm firmware and MR semantics accept that sentinel.
- Several builders write directly into circular DMA queues and only some variable-length regions handle wraparound; fixed header size assumptions are enforced for write-completion WRs but should remain guarded.
- `c4iw_post_send` accesses `wr->sg_list[0]` in some opcode paths and fast-path predicates; zero-SGE edge cases need coverage.
- User QP flushing cannot snapshot user queue state, so it marks CQ/QP error and relies on userspace to observe error state rather than generating per-WR flush CQEs.
- Doorbell flow-control paths split locking between xarray lock and QP lock; lock ordering must remain consistent with adapter DB recovery code.

## Test Signals

Tests should cover QP create/destroy for kernel, userspace, SRQ, and on-chip SQ paths; mmap key creation; post-send opcodes including SEND, WRITE, WRITE_WITH_IMM, READ, READ_WITH_INV, REG_MR, LOCAL_INV, and write-completion coalescing; RQ/SRQ posting with wraparound; state transitions IDLE/RTS/CLOSING/TERMINATE/ERROR; flush/drain CQE generation; doorbell-off deferral; resource unwind injection; and RDMA CM connect/disconnect integration.
