# sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_ib_sysfs.h

Purpose: sysfs API declarations for usNIC RDMA device and QPN reporting.

Important APIs: declares PF sysfs register/unregister, QP group QPN add/remove helpers, and exported `usnic_attr_group`.

Control flow: main PF lifecycle calls register/unregister; QP group lifecycle calls QPN add/remove; `usnic_dev_ops.device_group` points to `usnic_attr_group`.

State and persistence: no state in the header; implementation owns kobject and attribute state.

Dependencies and integration: includes `usnic_ib.h`, tying sysfs callbacks to PF and QP group structures.

Risks: callers must pair register/unregister and add/remove to avoid kobject leaks or dangling sysfs files.

Test signals: build linkage and sysfs lifecycle under module load/unload and QP create/destroy.
