# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnge/bnge_auxr.c

Purpose: Implements `bnge` auxiliary-bus integration for RDMA/RoCE clients and exposes a firmware-message bridge for the auxiliary driver.

Important APIs/functions: `bnge_rdma_aux_device_init()` allocates IDA id, auxiliary device, `bnge_auxr_dev`, and `bnge_auxr_info`, initializes the aux device, populates shared hardware info, and clears RoCE flags on failure. `bnge_rdma_aux_device_add()`, `bnge_rdma_aux_device_del()`, and `bnge_rdma_aux_device_uninit()` manage auxiliary bus lifetime. `bnge_register_dev()` grants requested MSI-X vectors after checking resources and fills `bnge_msix_info`. `bnge_unregister_dev()` clears allocation state. `bnge_send_msg()` sends arbitrary HWRM command payloads through the L2 driver's request path.

Control flow: PCI probe initializes aux state after doorbell BAR mapping and adds the aux device after netdev allocation. RDMA client registration occurs later through exported symbols, under `netdev_lock()` and aux mutex. Removal deletes the aux device before freeing netdev/IRQs, then uninitializes it.

State/persistence: `bnge_dev` keeps `aux_priv` and `auxr_dev`; `bnge_auxr_dev` stores PCI/net/bar/doorbell/RoCE/stat/PF data and a lock; `bnge_auxr_info` stores client handle and MSI-X request count. IDA ids persist until device release.

Dependencies/integration: Uses Linux auxiliary bus, PCI drvdata, netdev locking, HWRM request helpers, IRQ table/resource checks from sibling files, and exports symbols for the RDMA auxiliary driver.

Risks/test signals: Lifetime ordering is delicate: delete/uninit/release must not race RDMA clients or netdev teardown. `bnge_send_msg()` trusts caller payload lengths and response buffer size. Test RoCE disabled/enabled probe, auxiliary add failure, RDMA register/unregister, insufficient resources, removal while client loaded, HWRM timeout path, and IDA leak checks.
