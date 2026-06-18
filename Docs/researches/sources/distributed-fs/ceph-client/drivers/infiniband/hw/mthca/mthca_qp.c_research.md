# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_qp.c

Purpose: implements mthca queue pair allocation, state transitions, querying, send/receive posting, special QP handling, event dispatch, and QP table lifetime management.

Important APIs/functions: exports `mthca_query_qp`, `mthca_modify_qp`, `mthca_alloc_qp`, `mthca_alloc_sqp`, `mthca_free_qp`, `mthca_tavor_post_send`, `mthca_tavor_post_receive`, `mthca_arbel_post_send`, `mthca_arbel_post_receive`, `mthca_free_err_wqe`, `mthca_init_qp_table`, `mthca_cleanup_qp_table`, and `mthca_qp_event`. It defines firmware QP context/path structures, state/transport mappings, and opcode conversion tables.

Control flow: allocation sizes SQ/RQ WQEs, maps mem-free QP/EQP/RDB ICM, allocates/registers kernel WQE buffers, allocates mem-free doorbells, initializes WQE rings, and publishes the QP in `dev->qp_table.qp`. Modify validates RDMA core state transitions, builds a firmware `mthca_qp_param`, handles path/GRH/access/PSN/CQ/SRQ fields, calls `mthca_MODIFY_QP`, updates cached state, and opens/closes the IB port for QP0 transitions. Posting paths lock SQ/RQ rings, check overflow against CQ-updated tails, build WQE segments by transport/opcode, write WRIDs, use memory barriers, then ring Tavor MMIO doorbells or Arbel doorbell records plus MMIO.

State and persistence: QP runtime state includes QPN allocation, hardware QP context, WQE buffers, WRID arrays, SQ/RQ head/tail/next pointers, mem-free doorbell records, cached access/port/state fields, special-QP header DMA buffers, and table refcounts. State persists in HCA context until reset/destroy.

Dependencies and integration: called by provider QP verbs and CQ cleanup; uses `mthca_memfree`, `mthca_wqe`, AH helpers, MR/buffer allocation, RDMA core QP validation, firmware commands (`QUERY_QP`, `MODIFY_QP`, `CONF_SPECIAL_QP`, `INIT_IB`, `CLOSE_IB`), and cached P_Key/GID data.

Risks: WQE construction is highly ordering-sensitive; missing barriers or bad doorbell counts can expose incomplete descriptors to hardware. The code has comments noting missing state checks in post paths. Special QP MLX header construction depends on PD `ntmr` and cached pkeys. Error unwind must coordinate CQ locks and QP table removal to avoid completion use-after-free.

Test signals: RC/UC/UD traffic, QP modify transition matrix, QP0/QP1 MAD traffic, Tavor and Arbel posting paths, send/receive overflow, CQ cleanup after reset/error, path migration events, atomics/RDMA writes/reads, and lockdep around QP destroy versus polling/events.
