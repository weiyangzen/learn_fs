# sources/distributed-fs/ceph-client/include/linux/qed/iwarp_common.h

Purpose: provides small iWARP firmware constants shared by the QED RDMA implementation, mainly connection mode identifiers, shared queue page layout, WQE sizing limits, and maximum QP count.

Important APIs/types/functions: includes `rdma_common.h` and defines `IWARP_ACTIVE_MODE`, `IWARP_PASSIVE_MODE`, `IWARP_SHARED_QUEUE_PAGE_SIZE`, RQ/SQ PBL offsets and maximum sizes within that shared page, `IWARP_REQ_MAX_INLINE_DATA_SIZE`, `IWARP_REQ_MAX_SINGLE_SQ_WQE_SIZE`, and `IWARP_MAX_QPS`.

Control flow: RDMA/iWARP setup code uses these constants while allocating shared queue pages, laying out RQ/SQ PBL regions, sizing inline data/WQEs, and distinguishing active versus passive MPA connection setup.

State and persistence: no state is stored here. The constants constrain DMA memory layout and firmware resource allocation for iWARP queue pairs and requests.

Dependencies and integration points: depends on `linux/qed/rdma_common.h`. It is conceptually paired with `qed_rdma_if.h` iWARP connection-management operations and firmware RDMA context setup.

Risks: incorrect offsets or maximum sizes can overlap queue regions inside the shared page or allow WQEs firmware cannot parse. `IWARP_MAX_QPS` must match firmware/ILT resource assumptions.

Test signals: compile iWARP-enabled RDMA builds, create active and passive iWARP connections, test inline sends near 128 bytes, stress SQ/RQ PBL allocation, and verify maximum resource negotiation does not exceed firmware-supported QP limits.
