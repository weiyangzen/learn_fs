# sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/verbs.h

## Purpose

`verbs.h` declares the IRDMA driver-private wrappers around RDMA core objects and exposes a small set of helpers shared between `verbs.c`, `utils.c`, and other driver modules. It is the main type contract for ucontext, PD, AH, MR/PBL, SRQ, CQ, QP, mmap entries, firmware-version helpers, completion opcode translation, multicast MAC helpers, device registration, QP events, and generated completions.

## Important APIs, Types, and Functions

- `struct irdma_ucontext` extends `ib_ucontext` with the owning IRDMA device, doorbell mmap entry, per-context CQ/QP/SRQ registered-memory lists and locks, ABI version, legacy mode, and raw-attribute mode.
- `struct irdma_pd`, `struct irdma_ah`, `struct irdma_mr`, `struct irdma_srq`, `struct irdma_cq`, and `struct irdma_qp` are the driver wrappers installed through `INIT_RDMA_OBJ_SIZE`.
- `struct irdma_pbl` and nested `irdma_qp_mr`, `irdma_cq_mr`, and `irdma_srq_mr` represent user memory registrations used as queue backing memory.
- `struct irdma_cq_buf` and `struct irdma_cmpl_gen` support CQ resize buffer lifetime and software-generated completions.
- `struct irdma_user_mmap_entry` records BAR offsets and cacheability for RDMA mmap entries.
- `irdma_fw_major_ver` and `irdma_fw_minor_ver` decode firmware version fields from `dev->feature_info`.
- `set_ib_wc_op_sq`, `set_ib_wc_op_rq`, and `set_ib_wc_op_rq_gen_3` translate internal completion operation types into RDMA core `ib_wc_opcode` values.
- Function prototypes expose registration, unregister, dealloc, QP event, generated flush completion, generated completion polling, and multicast MAC APIs.

## Control Flow

The header does not implement object lifecycles directly, but its structures define how lifecycle code moves state. Ucontext memory registrations are inserted into type-specific lists during MR registration and removed when QP/CQ/SRQ creation consumes them. QPs link RDMA core state, low-level `irdma_sc_qp`, CQs, PD, CM node, offload context, push mmap entries, workqueue/timer state, and kernel/user ring memory. CQs hold the low-level CQ, coherent memory or user memory state, a refcount completion used by async interrupt paths, resize buffers, and generated completions. MR/PBL fields allow one object shape to represent application MRs, memory windows, DMA MRs, and queue-memory registrations.

The inline WC helpers are called from CQ polling after low-level CQ parsing. SQ operation types map to write, read, send, register MR, atomic, and local invalidate completions. RQ mapping differs by hardware generation and send-with-immediate support: older iWARP treats immediate receive as RDMA-write-with-immediate, while gen3 uses low-level op types for receive-with-immediate.

## State and Persistence

The header defines runtime-only in-memory state. Important persistence boundaries are RDMA core object lifetimes, hardware resource IDs, mmap entries, DMA memory references, refcounts/completions, and queue ring state. It also encodes bitfields such as `user_mode`, `is_hwreg`, `dma_mr`, `pbl_allocated`, `on_list`, `flush_issued`, `hte_added`, `suspend_pending`, and `rts_ae_rcvd` that drive teardown and state transitions.

## Dependencies and Integration Points

The types embed RDMA core objects (`ib_ucontext`, `ib_pd`, `ib_ah`, `ib_mr`, `ib_mw`, `ib_srq`, `ib_cq`, `ib_qp`) and low-level IRDMA objects (`irdma_sc_*`, `irdma_*_uk`, PBLE, DMA, AH, and QP context structures). They are consumed by `main.h` container helpers, `verbs.c` object operations, `utils.c` CQP and completion paths, CM code, and low-level hardware programming code.

## Risks

Because these structures define cross-file ownership, layout and flag changes have broad blast radius. Refcount and completion fields must remain paired with table publication/removal rules. Queue-memory PBL fields are type-dependent, so using a CQ PBL as a QP PBL or failing to update `on_list` can corrupt later object creation. Opcode mapping helpers are small but user-visible through CQ polling; wrong mappings break application completion semantics. Bitfield state is compact but easy to update without proper locking if callers do not follow the surrounding `verbs.c` and `utils.c` protocols.

## Test Signals

Compile-time signals include all container conversions, object-size registration, and prototypes matching definitions. Runtime signals include CQ polling opcode correctness for SQ/RQ, gen2 versus gen3 immediate-data receives, QP/CQ refcount completion under destroy, queue-memory registration consumption from ucontext lists, push mmap lifecycle, generated flush completion delivery, and correct firmware version reporting.
