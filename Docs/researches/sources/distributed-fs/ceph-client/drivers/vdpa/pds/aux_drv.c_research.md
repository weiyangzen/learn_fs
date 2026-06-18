<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/pds/aux_drv.c -->
# sources/distributed-fs/ceph-client/drivers/vdpa/pds/aux_drv.c

Purpose: Implements module init/exit and auxiliary-bus probe/remove for AMD/Pensando vDPA VFs exposed by the PDS core driver.

Important APIs/functions: `pds_vdpa_probe()` allocates `struct pds_vdpa_aux`, validates VF ID, obtains management identity via `pds_vdpa_get_mgmt_info()`, probes modern virtio PCI config with `vp_modern_probe()`, registers `vdpa_mgmtdev_register()`, and creates debugfs entries. `pds_vdpa_remove()` unregisters the management device, releases IRQs, removes virtio PCI modern mappings, tears down debugfs, and frees memory. Module init/exit wrap `auxiliary_driver_register()` and debugfs root creation/destruction.

Control flow: The PDS core publishes an auxiliary device named for vDPA. Probe captures the parent `pds_auxiliary_dev`, derives `vf_id` from the VF PCI device, asks firmware for vDPA identity, probes virtio config space on the VF, and only then registers with the generic vDPA management layer. Error paths unwind in reverse order: virtio remove, IRQ vector free, memory free, drvdata clear.

State and persistence: `struct pds_vdpa_aux` is the per-auxiliary-device anchor and stores the PDS auxiliary device, `vdpa_mgmt_dev`, active `pds_vdpa_device`, firmware identity, VF ID, debugfs dentry, virtio modern device, and interrupt count.

Dependencies and integration points: Uses Linux auxiliary bus, PCI, vDPA, virtio PCI modern helpers, and PDS common/core/adminq/auxbus APIs. It is the registration bridge between the PDS PF adminq service and generic vDPA user-visible management.

Risks: Probe ordering is important: debugfs identity assumes `pds_vdpa_get_mgmt_info()` succeeded, and management registration assumes `vp_modern_probe()` found valid virtio regions. Remove calls `pds_vdpa_release_irqs(vdpa_aux->pdsv)` safely with possible NULL, but removal during an active vDPA device relies on management unregister deleting child devices first.

Test signals: Auxiliary probe should create a management device and debugfs directory for the VF. Failure injection for identity command, virtio modern probe, and management registration should unwind without leaked IRQ vectors or stale drvdata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/pds/aux_drv.c -->
