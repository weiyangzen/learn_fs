# sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/user.h

## Purpose
This header defines the IRDMA shared user/kernel queue ABI types and constants: handles, access flags, operation codes, async event codes, device limits, completion status enums, post structures, CQ poll results, UK QP/CQ/SRQ structures, function prototypes, and AE-to-flush error mapping.

## Important APIs, Types, And Functions
- Handle aliases and memory access flags define local/remote read/write, bind-window, and zero-based access semantics.
- Operation codes cover RDMA write/read, send variants, bind MW, fast register, invalidate, NOP, atomics, and receive completions.
- Async event constants classify AMP, UDA, CQ, RDMA/DDP/RoCE, LLP, reset, terminate, catastrophic, suspend, and adapter failures.
- Device capability constants define WQE/CQE/AEQE sizes, max QP/CQ/CEQ ids, max fragments, max message sizes, max inline data, Q2/QP context sizes, and queue limits.
- Work request structures include `irdma_post_sq_info`, `irdma_post_send`, `irdma_rdma_write`, `irdma_rdma_read`, `irdma_bind_window`, atomics, local invalidate, and `irdma_post_rq_info`.
- Queue structures include `irdma_ring`, `irdma_qp_uk`, `irdma_cq_uk`, `irdma_srq_uk`, init-info structs, `irdma_sq_uk_wr_trk_info`, `irdma_qp_quanta`, `irdma_cqe`, and `irdma_extended_cqe`.
- `irdma_ae_to_qp_err_code()` maps hardware AE ids to flush codes and QP event types.

## Control Flow
The header is mostly declarative. `uk.c` consumes these structures to post WQEs and poll CQEs. Callers fill `irdma_post_sq_info` with operation-specific union data and flags; post functions validate and encode it. Completion polling fills `irdma_cq_poll_info`. The inline AE mapping switch converts low-level AE ids into the completion flush code/event type exposed to upper layers.

## State And Persistence
The UK structures persist for QP/CQ/SRQ lifetimes and may be shared with user mappings depending on the wider driver path. They store ring positions, queue bases, doorbells, WR ids, shadow areas, polarity, flush/destroy state, queue caps, and generation-specific operation tables. Constants here define the stable numeric protocol between driver code, hardware descriptors, and user/kernel queue handling.

## Dependencies And Integration Points
The header depends on Linux integer types, `struct ib_sge`, spinlocks, MMIO pointers, and hardware attribute definitions from other IRDMA headers. It is included by `uk.c`, `type.h`, and higher layers that construct WRs or interpret completions.

## Risks And Edge Cases
Because this file is ABI-like, changing constants, enum numeric values, structure layout, or operation codes can break userspace/provider compatibility. AE mapping defaults unknown events to general fatal/catastrophic behavior, which is conservative but may hide new precise error types. Queue structures hold raw pointers and MMIO addresses, so initialization must be complete before use.

## Test Signals
Compile tests should catch prototype drift. ABI/layout review, userspace verbs tests, CQ error/flush tests for many AE codes, max-SGE and inline boundary tests, and mixed kernel/user queue operation coverage are the important signals.
