# sources/distributed-fs/ceph-client/drivers/vfio/iommufd.c

## Purpose

`iommufd.c` provides VFIO helper operations for binding devices to IOMMUFD and attaching IO address spaces. It supports physical-device bindings and emulated/mdev-style access bindings, plus legacy group compatibility IOAS helpers.

## Important APIs, Types, and Functions

Compatibility helpers include `vfio_iommufd_device_has_compat_ioas()`, `vfio_df_iommufd_bind()`, `vfio_iommufd_compat_attach_ioas()`, and `vfio_df_iommufd_unbind()`. Physical-device helpers are `vfio_iommufd_physical_bind()`, `vfio_iommufd_physical_unbind()`, `vfio_iommufd_physical_attach_ioas()`, `vfio_iommufd_physical_detach_ioas()`, and PASID attach/detach variants. Emulated-device helpers are `vfio_iommufd_emulated_bind()`, `vfio_iommufd_emulated_unbind()`, `vfio_iommufd_emulated_attach_ioas()`, and detach. Exported query helpers expose a device's IOMMUFD context and device id.

## Control Flow

Physical bind calls `iommufd_device_bind()` on `vdev->dev`, stores the iommufd device, and initializes a PASID IDA. Attach either attaches or replaces the non-PASID IOAS and sets `iommufd_attached`. PASID attach tracks attached PASIDs in an IDA and replaces an existing PASID or attaches a new one. Physical unbind detaches all PASIDs, detaches the non-PASID IOAS if present, unbinds the iommufd device, and clears the pointer.

Emulated bind creates an `iommufd_access` object with unmap callback `vfio_emulated_unmap()`, which forwards to driver `dma_unmap` when present. Emulated attach/replace uses `iommufd_access_attach()` or replace and marks `iommufd_attached`; detach calls `iommufd_access_detach()`.

## State and Persistence Behavior

State is stored in `struct vfio_device`: `iommufd_device`, `iommufd_access`, `iommufd_attached`, and PASID IDA. Attachments persist for the open VFIO device file and are destroyed on unbind/close. No file-backed persistence exists.

## Dependencies and Integration Points

The file imports the `IOMMUFD` and `IOMMUFD_VFIO` namespaces and depends on VFIO device ops, iommufd device/access APIs, IOMMU group checks, and the device-set lock held by callers.

## Risks and Edge Cases

Every function assumes `dev_set->lock` where stated. Physical unbind loops through all PASIDs and must run before destroying the IDA users. `vfio_iommufd_get_dev_id()` distinguishes an owned device with no id (`-ENOENT`) from a device not owned by the context (`-ENODEV`). No-IOMMU returns success for bind/attach compatibility without creating real translations, relying on higher-level CAP and IOAS checks.

## Test Signals

Test physical bind/unbind, attach/replace/detach, PASID attach/replace/detach, unbind with active PASIDs, emulated bind/attach/detach/unmap callback, compat IOAS attach for group path, no-IOMMU shortcuts, exported device id query for same context/group context/unowned context, and lockdep coverage for device-set locking.
