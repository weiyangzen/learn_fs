# sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_ib_verbs.h

Purpose: declarations for usNIC RDMA verbs callbacks registered in `usnic_dev_ops`.

Important APIs: declares link layer, device/port/QP/GID query, PD lifecycle, QP create/destroy/modify, CQ create/destroy, MR register/deregister, ucontext lifecycle, and mmap callbacks.

Control flow: `usnic_ib_main.c` includes this header and wires each function into RDMA core operations. RDMA core invokes the implementation in `usnic_ib_verbs.c`.

State and persistence: no state here; concrete object state is in `usnic_ib.h` and QP group/UIOM structures.

Dependencies and integration: includes `usnic_ib.h` for object containers and RDMA types.

Risks: callback signatures must track RDMA core API changes. The header does not reveal unsupported operations, so behavior is defined by implementation.

Test signals: compile coverage of `usnic_dev_ops` assignments and uverbs lifecycle tests reaching each callback.
