<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/pds/debugfs.h -->
# sources/distributed-fs/ceph-client/drivers/vdpa/pds/debugfs.h

Purpose: Declares the PDS vDPA debugfs lifecycle functions.

Important APIs: Root management functions `pds_vdpa_debugfs_create()` and `destroy()`, PCI/identity creation functions, vDPA device file add/delete, and vDPA debugfs reset.

Control flow: `aux_drv.c` calls root create/destroy at module init/exit and base debugfs creation at probe. `vdpa_dev.c` calls vDPA add/reset around `dev_add` and `dev_del`.

State and persistence: No state in the header; functions manage in-kernel debugfs dentries.

Dependencies and integration points: Includes `linux/debugfs.h` and expects `struct pds_vdpa_aux` from the shared PDS driver context.

Risks: Header users must call functions in lifecycle order; reset assumes a valid auxiliary object and rebuilds base entries.

Test signals: Compile-time linkage and runtime debugfs directory creation/removal validate the contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/pds/debugfs.h -->
