<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/pds/aux_drv.h -->
# sources/distributed-fs/ceph-client/drivers/vdpa/pds/aux_drv.h

Purpose: Declares the per-auxiliary-device state and driver naming constants for the PDS vDPA driver.

Important APIs/types: `PDS_VDPA_DRV_DESCRIPTION` and `PDS_VDPA_DRV_NAME` feed module and debug naming. `struct pds_vdpa_aux` stores the parent `pds_auxiliary_dev`, registered `vdpa_mgmt_dev`, active `pds_vdpa_device`, firmware identity block, VF ID, debugfs dentry, `virtio_pci_modern_device`, and allocated interrupt count.

Control flow: This header is included by probe, debugfs, command, and device files so they share the same auxiliary state anchor.

State and persistence: Pure runtime state; no persistent storage. The `pdsv` pointer is NULL until `dev_add`, and `nintrs` tracks whether MSI-X vectors must be freed.

Dependencies and integration points: Includes `linux/virtio_pci_modern.h` and relies on PDS types from included C files. It connects the PDS auxiliary bus object with the vDPA management object and virtio PCI modern config access.

Risks: Ownership is split: `aux_drv.c` owns allocation/free of `pds_vdpa_aux`, while `vdpa_dev.c` owns the child `pds_vdpa_device` and writes `vdpa_aux->pdsv`. Bugs in that handoff can produce stale debugfs/private pointers.

Test signals: Compile-time signal is clean inclusion by all PDS C files; runtime signal is correct NULL/non-NULL `pdsv` transitions during `vdpa dev add/del`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/pds/aux_drv.h -->
