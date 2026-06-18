# sources/distributed-fs/ceph-client/drivers/infiniband/hw/ocrdma/ocrdma_verbs.h

## Purpose
`ocrdma_verbs.h` is the OCRDMA provider's verbs interface header. It declares the functions that `ocrdma_main.c` and the RDMA core operation table use to bind OCRDMA device objects to generic InfiniBand/RDMA verbs.

## Important APIs, Types, And Functions
The header declares posting APIs (`ocrdma_post_send`, `ocrdma_post_recv`, `ocrdma_post_srq_recv`), CQ APIs (`ocrdma_poll_cq`, `ocrdma_arm_cq`, `ocrdma_create_cq`, `ocrdma_resize_cq`, `ocrdma_destroy_cq`), query APIs (`ocrdma_query_device`, `ocrdma_query_port`, `ocrdma_query_protocol`, `ocrdma_query_pkey`), context and mmap APIs, PD APIs, QP APIs including `_ocrdma_modify_qp`, SRQ APIs, and MR APIs (`ocrdma_get_dma_mr`, `ocrdma_reg_user_mr`, `ocrdma_alloc_mr`, `ocrdma_map_mr_sg`, `ocrdma_dereg_mr`). It references RDMA core types such as `ib_qp`, `ib_cq`, `ib_wc`, `ib_udata`, `uverbs_attr_bundle`, `ib_mr`, and `scatterlist`.

## Control Flow
There is no executable control flow in this file. Its declarations define the call surface used by the driver's registration code and by other OCRDMA modules. The functions are implemented mostly in `ocrdma_verbs.c`, while `ocrdma_query_protocol` is expected from another OCRDMA source file.

## State And Persistence Behavior
The header stores no state. Its importance is contractual: prototype drift against RDMA core operation signatures or against `ocrdma_verbs.c` would break compilation or runtime operation registration.

## Dependencies And Integration Points
The file assumes `ocrdma_qp` and RDMA core types are already visible through included OCRDMA/RDMA headers in including translation units. It is integrated by the OCRDMA main provider setup that fills `ib_device_ops`, and it also exposes `ocrdma_del_flush_qp` for flush-list cleanup outside the core verbs implementation.

## Risks And Test Signals
Risks are API mismatch with evolving kernel RDMA signatures, missing include dependencies if the header is included from a narrower context, and stale declarations for functions implemented elsewhere. Test signals are successful kernel build with `CONFIG_INFINIBAND_OCRDMA`, sparse/C=1 prototype checks, and exercising every registered `ib_device_ops` entry through RDMA core smoke tests.
