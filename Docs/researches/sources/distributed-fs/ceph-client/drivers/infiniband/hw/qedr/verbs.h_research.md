# sources/distributed-fs/ceph-client/drivers/infiniband/hw/qedr/verbs.h

Purpose: public verbs declaration header for the qedr RDMA driver. It exposes the function surface implemented in `verbs.c` for registration in qedr `ib_device_ops` and use by adjacent qedr CM/GSI code.

Important APIs/types: declares query APIs, ucontext/mmap/PD/XRCD lifecycle, CQ create/destroy/arm/poll, QP create/modify/query/destroy/post send/post recv, SRQ create/modify/query/destroy/post receive, AH create/destroy, MR registration/allocation/map/deregistration, MAD processing, and `qedr_port_immutable()`.

Control flow: the main qedr device setup includes this header and assigns these callbacks into RDMA core operations. Runtime calls originate from RDMA core/uverbs and land in `verbs.c`; no inline logic or state is stored here.

State and persistence: no state. Persistence is delegated to structures declared in `qedr.h` and allocated/manipulated by the implementation.

Dependencies and integration: relies on RDMA core types such as `ib_device`, `ib_udata`, `uverbs_attr_bundle`, `ib_qp`, `ib_mr`, and `rdma_user_mmap_entry`, plus kernel `scatterlist` and VM types supplied by includers.

Risks: prototypes are the contract between qedr registration and implementation; signature drift with RDMA core APIs will break builds. The header does not encode sequencing constraints, so callers must still respect RDMA core object lifetimes.

Test signals: compile coverage of all `ib_device_ops` assignments, module load, and rdma-core lifecycle tests that exercise each declared callback.
