# sources/distributed-fs/ceph-client/drivers/accel/amdxdna/amdxdna_pci_drv.c

Purpose: implements the AMD XDNA PCI DRM accel driver: PCI ID matching, DRM driver registration, per-file client lifecycle, ioctls, GEM integration, IOMMU/notifier setup, sysfs setup, runtime/system PM hooks, and probe/remove.

Important APIs/functions: `amdxdna_drm_drv` defines DRM features, file operations, ioctls, open/close, GEM create, and prime import. `amdxdna_probe()` allocates the DRM device, selects `amdxdna_dev_info` by device/revision, initializes locks/lists/IOMMU/notifier workqueue, calls hardware ops init, creates sysfs, and registers DRM. `amdxdna_remove()` unplug/unregisters, cleans clients, finalizes hardware, and tears down IOMMU. `amdxdna_drm_open()` allocates `amdxdna_client`, binds SVA/PASID unless forced IOVA, initializes SRCU/xarray/mm lock, and links into client list. `amdxdna_client_cleanup()` removes contexts, heap, SVA, mm refs, and client memory.

Control flow: `/dev/accel` open enters `accel_open()` then DRM open callback. Ioctls dispatch to context, BO, exec, get-info/get-array, and privileged set-state handlers. PM callbacks call generic AMD XDNA PM functions.

State and persistence: `amdxdna_dev` stores DRM device, selected hardware info, handle, XRS solver, locks, clients, firmware version, notifier state, and IOMMU state. Each file has an `amdxdna_client`. Runtime only.

Dependencies: PCI, DRM accel core, DRM GEM/scheduler/ioctl, IOMMU SVA, AMD XDNA hardware ops, sysfs, PM.

Risks: close path returns early if `drm_dev_enter()` fails, which can leave cleanup to remove path. Client cleanup occurs under `dev_lock`; operations that drop/reacquire the lock must preserve ordering. Set-state is `DRM_ROOT_ONLY`.

Test signals: probe/remove all supported IDs/revisions, open failure paths for SVA/PASID, ioctl validation, runtime/system suspend, forced IOVA mode, remove with open clients, and sysfs/DRM node registration.
