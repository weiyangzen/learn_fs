# sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_ib.h

Purpose: central usNIC RDMA object definitions and container helpers.

Important APIs/types: defines one-port/one-completion-vector constants, module parameter `usnic_ib_share_vf`, `struct usnic_ib_ucontext`, `struct usnic_ib_pd`, `struct usnic_ib_cq`, `struct usnic_ib_mr`, `struct usnic_ib_dev`, `struct usnic_ib_vf`, container conversion helpers, `usnic_ib_log_vf()`, and `UPDATE_PTR_LEFT`.

Control flow: RDMA core allocates objects sized through `INIT_RDMA_OBJ_SIZE`; verbs callbacks convert generic IB objects to usNIC-specific containers. PF/VF management and QP group code use these structures for device, context, PD, MR, and VF ownership.

State and persistence: `usnic_ib_dev` holds PF netdev/PCI/forwarding device, VF list, user context list, lock, VF resource counts, kref, and QPN sysfs root. `usnic_ib_vf` tracks one VF vNIC, QP group refcount, bound PD, and lock. Ucontexts own QP group lists; PDs own UIOM protection domains.

Dependencies and integration: depends on RDMA core, IOMMU, netdevice, usNIC ABI, and vNIC resource headers. It is the shared contract among main, verbs, QP group, sysfs, UIOM, and forwarding code.

Risks: locking rules are implicit in comments and code: context/QP group lists are protected by `usdev_lock`, VF bind/refcount by `vf->lock`, and QP group flow state by its spinlock. Violating those rules risks list corruption or IOMMU detach while resources are active.

Test signals: RDMA object allocation/free paths, VF sharing enabled/disabled, context teardown with empty QP group list, and lockdep on QP create/destroy/remove paths.
