# sources/distributed-fs/ceph-client/drivers/infiniband/hw/bnxt_re/qplib_fp.h

## Purpose
`qplib_fp.h` declares the fast-path data model and exported APIs for bnxt_re queue objects. It describes software work requests, scatter-gather elements, QP/CQ/SRQ/NQ state, completion records, queue sizing helpers, CQ/NQ valid-bit tests, and the public functions implemented by `qplib_fp.c`.

## Important APIs, types, and functions
Key types are `bnxt_qplib_srq`, `bnxt_qplib_sge`, `bnxt_qplib_swq`, `bnxt_qplib_swqe`, `bnxt_qplib_q`, `bnxt_qplib_qp`, `bnxt_qplib_cqe`, `bnxt_qplib_cq`, `bnxt_qplib_nq_db`, `bnxt_qplib_nq`, and `bnxt_qplib_nq_work`. It defines work request type constants for send, send with immediate, RDMA write/read, atomics, local invalidate, fast-reg MR, bind MW, receive, and receive with immediate. It exposes helpers such as `bnxt_qplib_queue_full()`, `bnxt_qplib_get_swqe()`, `bnxt_qplib_get_depth()`, `bnxt_qplib_set_sq_size()`, `bnxt_qplib_calc_ilsize()`, `bnxt_re_update_msn_tbl()`, `__is_var_wqe()`, and `__is_err_cqe_for_var_wqe()`.

## Control flow
The header defines contracts used across verbs and qplib. Callers allocate and fill `bnxt_qplib_swqe`, then invoke post helpers. Create helpers consume the queue sizing fields in `bnxt_qplib_qp`, `bnxt_qplib_cq`, or `bnxt_qplib_srq`. Completion polling returns normalized `bnxt_qplib_cqe` records. Inline helpers compute queue depth in slots, translate hardware queue-full deltas, and maintain the software queue circular index.

## State and persistence
All structures are in-memory driver state, but many fields mirror firmware state: QP IDs, CQ IDs, SRQ IDs, DPI values, access flags, PSNs, MTU, retry counters, destination addressing, VLAN, SGID index, and queue doorbell state. HWQ members point to DMA or user memory backing real hardware queues. Toggle bits and valid-bit macros persist only as producer/consumer interpretation state.

## Dependencies and integration points
The header depends on `rdma/bnxt_re-abi.h` and hardware descriptor definitions from included C files. It is included by `main.c`, `ib_verbs.c`, `hw_counters.c`, `qplib_fp.c`, `qplib_rcfw.c`, and slow-path code. Its API is the boundary between RDMA core wrappers and low-level queue programming.

## Risks
Because this header defines packed hardware-facing layouts and queue math, small field or macro mistakes affect the entire fast path. The snapshot contains duplicated members (`single`) and a duplicated `typedef` line for `srqn_handler_t`, which would be compile-break risks if present in the active tree. `bnxt_qplib_queue_full()` deliberately allows false-full behavior, so callers must retry correctly. Slot/depth calculations differ between static and variable WQE modes and need bounds tests. Constants such as `BNXT_QPLIB_SWQE_MAX_INLINE_LENGTH` must stay consistent with firmware.

## Test signals
Compile tests should include TLV and non-TLV command users. Runtime tests should validate queue depth and slot calculations for static and variable WQEs, inline length clipping, RQ max-slot calculation, CQ/NQ valid-bit toggling, QP state/query mapping, SRQ free-list behavior, CQ coalescing limits, QP1 header sizes, and user/kernel DPI interactions.
