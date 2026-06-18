# sources/distributed-fs/ceph-client/drivers/infiniband/sw/siw/siw_verbs.h

Purpose: Declares the RDMA verbs entry points implemented by `siw_verbs.c` and a small SGL conversion helper. It is the interface consumed by `siw_main.c` when constructing `ib_device_ops` and by other SIW files that need event or mmap callbacks.

Important APIs/types/functions: `siw_copy_sgl()` copies RDMA-core `ib_sge` arrays into SIW ABI `siw_sge` arrays. Prototypes cover context, device, port, GID, PD, QP, CQ, MR, SRQ, mmap, and event functions: `siw_create_qp`, `siw_post_send`, `siw_post_receive`, `siw_poll_cq`, `siw_reg_user_mr`, `siw_alloc_mr`, `siw_map_mr_sg`, `siw_post_srq_recv`, `siw_qp_event`, `siw_cq_event`, `siw_srq_event`, and `siw_port_event`.

Control flow: `siw_main.c` binds most of these functions into the RDMA core ops table. `siw_qp.c`, `siw_qp_rx.c`, and `siw_qp_tx.c` call event helpers and rely on SGL layouts produced by post paths. CM uses QP event integration indirectly through state changes and errors.

State and persistence behavior: The header itself has no state. It defines the callable surface for code that allocates or mutates in-memory RDMA objects and user-mapped queues.

Dependencies/integration: Includes Linux errno, IWCM, ib verbs, user verbs, `siw.h`, and `siw_cm.h`. This creates a broad dependency surface; changes here ripple through provider registration and all compile units using verbs prototypes.

Risks: Prototype drift with RDMA core APIs breaks builds across kernel versions. `siw_copy_sgl()` assumes destination capacity has already been validated by the caller. Duplicate `siw_query_port` declaration is harmless but a maintenance smell.

Test signals: Full driver build against target kernel headers, sparse/checkpatch for prototype mismatches, create/post/query verbs smoke tests, and compile coverage with user and kernel resource paths.
