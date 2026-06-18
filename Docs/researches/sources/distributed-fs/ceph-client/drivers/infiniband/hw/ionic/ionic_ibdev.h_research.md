# sources/distributed-fs/ceph-client/drivers/infiniband/hw/ionic/ionic_ibdev.h

Purpose: central internal header for the Ionic RDMA driver. It defines driver limits, the main `struct ionic_ibdev`, object wrappers for RDMA core types, admin/EQ/CQ/QP/MR/AH state, helper conversions, and prototypes spanning admin, control path, datapath, stats, and page-table code.

Important APIs/types: key types are `struct ionic_ibdev`, `ionic_eq`, `ionic_aq`, `ionic_admin_wr`, `ionic_ctx`, `ionic_tbl_buf`, `ionic_pd`, `ionic_cq`, `ionic_vcq`, `ionic_qp`, `ionic_sq_meta`, `ionic_rq_meta`, `ionic_ah`, `ionic_mr`, `ionic_counter_stats`, and `ionic_counter`. Inline helpers convert RDMA core pointers back to Ionic containers, select user or kernel doorbell IDs, detect local-only opcodes, and complete QP/CQ krefs.

Control flow: every implementation file includes this header to share object layout and function contracts. RDMA core calls enter object wrappers, helpers recover Ionic private state, control path allocates resources and queues, datapath posts/polls them, stats binds counters to QPs, and page-table helpers fill MR/CQ/QP DMA mapping descriptors.

State and persistence: the header documents all runtime state ownership. `ionic_ibdev` owns global tables, ID allocators, admin/EQ vectors, reset state, and stats. `ionic_qp` owns SQ/RQ queues, metadata, flush state, CMB mappings, user umems, and addressing metadata. `ionic_cq` owns poll/flush queues, credits, color, arm counters, and optional umem.

Dependencies and integration: includes RDMA core headers, user ABI, Ionic Ethernet API/register headers, and local firmware/queue/resource/LIF config headers. It is the private ABI among all Ionic RDMA translation units.

Risks: broad sharing means layout changes can affect concurrency and teardown in multiple files. List heads embedded in QP/CQ objects must be initialized and removed consistently. The header repeats `IONIC_SPEC_HIGH`, which is harmless but signals the need for careful constants review. Conversion helpers assume RDMA core objects are always embedded in the declared wrappers.

Test signals: full driver build, sparse/lockdep checks, QP/CQ create/destroy with user and kernel queues, reset teardown, mmap lifecycle, and all verbs ops resolving to declared prototypes.
