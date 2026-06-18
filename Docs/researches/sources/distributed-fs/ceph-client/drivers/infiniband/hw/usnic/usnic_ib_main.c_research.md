# sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_ib_main.c

Purpose: module, PCI, PF/VF discovery, netdev/inet notifier, and RDMA device registration logic for Cisco usNIC.

Important APIs/functions: module globals `usnic_log_lvl` and `usnic_ib_share_vf`; `usnic_ib_log_vf()`; netdev/inet handlers; `usnic_port_immutable()`; `usnic_get_dev_fw_str()`; `usnic_dev_ops`; PF lifecycle `usnic_ib_device_add/remove()`, `usnic_ib_discover_pf()`, `usnic_ib_undiscover_pf()`; PCI probe/remove; module init/exit.

Control flow: module init registers PCI, netdev, inetaddr notifiers, initializes transport bitmap, and creates debugfs. PCI probe validates IOMMU mapping, enables/request regions for a VF, allocates `usnic_vnic`, discovers or creates the parent PF RDMA device, links the VF, and records per-VF resource counts. PF creation allocates an `ib_device`, forwarding device, netdev binding, sysfs group, initial MAC/MTU/link/IP state, node GUID, and RDMA ops. Netdev/IP events update forwarding state, transition active QP groups to ERR, and dispatch RDMA port/GID events. Remove reverses VF registration and drops the PF kref, unregistering PF when the last VF disappears.

State and persistence: global PF list and lock track registered PF devices. Each PF owns VF list, context list, forwarding state, sysfs QPN root, and kref. Module parameters persist until unload. Notifier-derived MAC/IP/link/MTU state persists in `ufdev`.

Dependencies and integration: ties together RDMA core, PCI, Cisco ENIC/vNIC resources, forwarding, UIOM, transport, debugfs, sysfs, and netdev/inet notifier APIs.

Risks: probe requires `device_iommu_mapped()`; without IOMMU no QPs are allowed. PF removal depends on accurate VF krefs. Netdev notifier uses `ib_device_get_by_netdev()` and must avoid lock inversions with rtnl; `query_port()` explicitly calls `ib_get_eth_speed()` before `usdev_lock` for that reason. Active QP groups are force-moved to ERR on address/link/reset changes.

Test signals: module load/unload ordering, PCI VF probe/remove, PF creation for first VF and destruction after last VF, notifier-driven GID/port events, IOMMU-disabled probe failure, sysfs/debugfs presence, and lockdep during netdev events plus QP churn.
