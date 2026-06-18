# sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_ib_sysfs.c

Purpose: sysfs reporting for usNIC PF devices and per-QPN/QP-group state.

Important APIs/functions: device attributes `board_id`, `config`, `iface`, `max_vf`, `qp_per_vf`, and `cq_per_vf`; QPN attributes `context` and `summary`; public APIs `usnic_ib_sysfs_register_usdev()`, `usnic_ib_sysfs_unregister_usdev()`, `usnic_ib_sysfs_qpn_add()`, and `usnic_ib_sysfs_qpn_remove()`.

Control flow: RDMA device registration exposes `usnic_attr_group`. PF discovery creates a `qpn` kobject under the RDMA device. QP group creation initializes/adds a kobject named by group ID; removal drops both QP and parent kobject refs. Attribute reads format PF/VF/resource configuration or QP group state/resource indices.

State and persistence: persistent sysfs state is the PF `qpn_kobj` and each QP group's embedded `kobj`. Attribute output reflects live `usnic_ib_dev` and `usnic_ib_qp_grp` state.

Dependencies and integration: depends on RDMA device kobjects, usNIC IB/QP group/vNIC helpers, and sysfs emit APIs. It is called from PF and QP group lifecycle code.

Risks: kobject reference balancing is subtle: register gets the RDMA device kobj, QPN add gets the parent qpn kobj, and remove/unregister put refs. Attribute reads access live QP group pointers; QP teardown must remove sysfs before freeing backing data. `config_show()` iterates resource types starting at EOL and relies on enum ordering.

Test signals: sysfs files under RDMA device, QPN entry create/remove under QP churn, kobject leak checks, and reading attributes during netdev/VF changes.
