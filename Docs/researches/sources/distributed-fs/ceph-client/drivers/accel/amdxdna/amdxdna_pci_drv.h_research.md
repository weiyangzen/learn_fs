# sources/distributed-fs/ceph-client/drivers/accel/amdxdna/amdxdna_pci_drv.h

Purpose: declares the shared AMD XDNA PCI driver structures, logging helpers, hardware operation callbacks, static device information, client state, IOMMU helpers, and device-info exports.

Important APIs/types: `struct amdxdna_dev_ops` is the hardware abstraction used by generic ioctls and PM: init/fini, suspend/resume, hwctx lifecycle/config/debug sync, HMM invalidate, command submit, AIE info/state, and array queries. `struct amdxdna_dev_info` records BAR indices, device memory geometry, vbnv string, device type, private per-generation data, and ops. `struct amdxdna_dev` embeds `drm_device` and stores device handle, solver, locks, client list, firmware version, notifier workqueue, and IOMMU state. `struct amdxdna_client` stores per-file PID, hwctx xarray/SRCU, file pointer, heap, SVA/PASID/mm, and memory usage counters.

Control flow: probe fills `amdxdna_dev`; open fills `amdxdna_client`; implementation files call through `dev_info->ops` to keep generic DRM code separate from AIE2 details.

State and persistence: structure definitions describe runtime state only. Device-info constants in register files are immutable tables.

Dependencies: DRM UAPI, DRM logging, Linux IOMMU/IOVA/workqueue/xarray.

Risks: `amdxdna_pm_resume_get_locked()` relies on `dev_lock` conventions declared here. `XDNA_MBZ_DBG()` validates must-be-zero ABI padding and should be used on new ioctls.

Test signals: compile all ops implementers, invalid padding tests, PASID/IOVA mode checks, and per-client memory accounting consistency.
