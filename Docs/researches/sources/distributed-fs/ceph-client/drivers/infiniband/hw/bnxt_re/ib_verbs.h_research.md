# sources/distributed-fs/ceph-client/drivers/infiniband/hw/bnxt_re/ib_verbs.h

Purpose: declares the private RDMA object wrappers and verbs callbacks implemented by `ib_verbs.c`.

Important APIs and types: wrapper structs embed RDMA-core objects and qplib state: `bnxt_re_pd`, `bnxt_re_ah`, `bnxt_re_srq`, `bnxt_re_qp`, `bnxt_re_cq`, `bnxt_re_mr`, `bnxt_re_mw`, `bnxt_re_ucontext`, `bnxt_re_user_mmap_entry`, `bnxt_re_dbr_obj`, and `bnxt_re_flow`. `bnxt_re_fence_data` stores the legacy fence MR/MW and bind WQE. `bnxt_re_gid_ctx` records hardware SGID index and refcount. Inline helpers compute send/receive WQE sizes, initialize queue depth according to user context capabilities, detect variable-WQE support, and convert zero-based port IDs to IB port numbers.

Control flow and integration: no major executable control flow exists in the header, but the prototypes define the driver's verbs surface: device/port query, GID/PKEY, PD/AH/SRQ/QP/CQ/MR/MW/ucontext/mmap/flow/MAD operations, CQ lock helpers, and mmap-entry insertion. RDMA-core operation tables in other driver files bind to these functions.

State and persistence: the wrapper structs define all long-lived per-object runtime state. Locks protect QP SQ/RQ, CQ polling, SRQ posting, and shared user page writes. User objects retain umem pointers and mmap entries until destroy/dealloc. GSI QPs retain packet header and send PSN state. No structure is persisted outside kernel memory.

Dependencies: depends on RDMA-core types, qplib queue/MR/CQ/SRQ/QP structures through included compilation units, and ABI constants used in user responses. It is included by debugfs and verbs implementation files.

Risks: object layout is central to `container_of()` conversions; changing embedded member names or lifetimes breaks many callbacks. The inline `bnxt_re_init_depth()` rounds depths unless userspace opted out, so queue sizing must stay aligned with ABI expectations. Variable-WQE capability depends on either user context masks or chip mode; mismatches can corrupt queue layout. Locking comments document intended protection and should remain accurate.

Test signals: compile coverage of all callback prototypes, uverbs ABI tests for user context capability masks and mmap entries, queue-depth tests with and without power-of-two rounding disabled, variable versus static WQE QP creation, lockdep around SQ/RQ/CQ/SRQ paths, and object lifecycle tests validating every wrapper is freed after its corresponding destroy callback.
