# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_provider.h

Purpose: defines the mthca RDMA-provider object wrappers and shared provider-side structures used by verbs implementations.

Important APIs/types/functions: declares access flag bits, `struct mthca_buf_list`, `union mthca_buf`, `struct mthca_uar`, `struct mthca_ucontext`, `struct mthca_mr`, `struct mthca_pd`, `struct mthca_eq`, `struct mthca_ah`, `struct mthca_cq`, `struct mthca_srq`, `struct mthca_wq`, `struct mthca_sqp`, and `struct mthca_qp`. It also provides `to_mucontext`, `to_mmr`, `to_mpd`, `to_mah`, `to_mcq`, `to_msrq`, and `to_mqp` container helpers.

Control flow: the header itself contains no runtime control flow except inline container conversions. Its embedded locking comment describes the CQ/QP table and object reference protocol used by event, completion, and destroy paths.

State and persistence: structures hold runtime state for RDMA objects: object numbers, DMA buffers/MRs, doorbell indices/records, WQ ring positions, WRID arrays, QP state/transport, special-QP headers, CQ resize buffers, refcounts, wait queues, spinlocks, and mutexes.

Dependencies and integration: included by provider, CQ, QP, SRQ, AH, EQ, and MR code; depends on RDMA core `ib_verbs.h` and packet/header packing helpers. The container helpers bridge generic `struct ib_*` objects to mthca private state.

Risks: lock ordering in the comment is part of the concurrency contract; violating it risks deadlock or use-after-free during completion/event/destroy races. Several fields are hardware-generation-specific, so callers must check mem-free/Tavor behavior before use.

Test signals: lockdep under CQ/QP event and destroy stress, RDMA object create/destroy loops, special QP traffic, CQ resize, and compile checks after RDMA core API changes.
