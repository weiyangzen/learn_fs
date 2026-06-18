# sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_ib_qp_grp.c

Purpose: manages usNIC QP groups, the abstraction that maps one userspace UD QP to VF resources, firmware filters, QP enablement, sysfs/debugfs entries, and UIOM PD/VF binding.

Important APIs/functions: `usnic_ib_qp_grp_state_to_string()`, dump helpers, `usnic_ib_qp_grp_create()`, `usnic_ib_qp_grp_modify()`, `usnic_ib_qp_grp_destroy()`, and `usnic_ib_qp_grp_get_chunk()`. Internals allocate/free vNIC resource chunks, create/release custom RoCE and UDP flows, enable/disable QPs, bind/unbind VF to UIOM PD, and derive QP group ID from flow port.

Control flow: create validates the requested resource spec against `min_transport_spec`, allocates WQ/RQ/CQ chunks from the VF vNIC, attaches the VF device to the PD's IOMMU domain on first group, initializes flow list/lock/state, creates the initial transport flow, derives `qp_num`, and registers sysfs. State transitions implement RESET/INIT/RTR/RTS/ERR: INIT creates or adds flows, RTR enables QPs, RTS is currently a no-op from RTR, RESET/ERR disable QPs and release flows as needed, and ERR dispatches `IB_EVENT_QP_FATAL`.

State and persistence: `struct usnic_ib_qp_grp` owns state, group ID/QPN, owner PID, resource chunk list, VF pointer, flow list, sysfs kobject, and forwarding device. Flow objects own firmware flow handles plus reserved RoCE ports or held UDP sockets. VF refcount and PD binding persist while groups are active.

Dependencies and integration: depends on vNIC resource allocation, forwarding devcmds, transport port/socket helpers, UIOM IOMMU attachment, sysfs QPN registration, debugfs flow files, and RDMA QP event callbacks.

Risks: state transition matrix is hand-coded and must keep firmware filters, QP enablement, sysfs/debugfs, socket refs, port reservations, and IOMMU attachment balanced. The code holds `qp_grp->lock` while creating/removing flows and calling forwarding/transport helpers, so blocking assumptions matter. `usnic_ib_qp_grp_destroy()` warns unless the group is already RESET.

Test signals: create/destroy loops for RoCE custom and UDP transports, INIT with additional filters, INIT->RTR->RTS->RESET transitions, ERR transition event delivery, VF sharing/refcount behavior, resource exhaustion, port reservation conflicts, UDP socket lifetime, and sysfs/debugfs cleanup.
