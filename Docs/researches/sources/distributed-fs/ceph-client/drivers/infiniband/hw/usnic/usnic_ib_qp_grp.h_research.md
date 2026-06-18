# sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_ib_qp_grp.h

Purpose: QP group data structures and API declarations for usNIC.

Important APIs/types: defines `struct usnic_ib_qp_grp`, `struct usnic_ib_qp_grp_flow`, external `min_transport_spec`, state/dump helpers, create/destroy/modify/get-chunk APIs, and `to_uqp_grp()`.

Control flow: verbs create/modify/destroy callbacks operate on `struct ib_qp` and convert to QP groups. QP group implementation uses fields declared here to track resources, flows, owner, state, and sysfs/debugfs objects.

State and persistence: header documents the persistent QP group state: IB QP wrapper, state, group ID, forwarding device, user context, flow list, resource chunks, owner PID, VF binding, list node, spinlock, and kobject. Flow state includes firmware flow pointer, transport-specific port/socket, parent group, list node, debugfs dentry, and dentry name.

Dependencies and integration: includes debugfs, RDMA verbs, usNIC IB structures, ABI, forwarding, and vNIC resource definitions.

Risks: object lifetime spans RDMA core, sysfs, debugfs, sockets, transport port bitmap, and vNIC resources; all users must observe the locking and teardown ordering implemented in `usnic_ib_qp_grp.c`.

Test signals: compile coverage, container conversion correctness, QP group sysfs/debugfs lifetime, and resource chunk lookup for WQ/RQ/CQ.
