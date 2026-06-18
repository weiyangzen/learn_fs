# sources/distributed-fs/ceph-client/drivers/vfio/cdx/main.c

## Purpose

`main.c` implements the VFIO bus driver for CDX devices. It wraps CDX resources as VFIO regions, exposes MSI IRQs through VFIO ioctls, handles device reset and bus-master control, maps MMIO regions to userspace, and registers/unregisters CDX devices with VFIO.

## Important APIs, Types, and Functions

`vfio_cdx_ops` is the VFIO device-ops table. It provides init/release, open/close, ioctl, region-info caps, device-feature, mmap, and iommufd physical bind/attach support. `vfio_cdx_open_device()` snapshots CDX resources into `struct vfio_cdx_region`, sets read/write/mmap flags, resets the device, and probes bus-master clear support. `vfio_cdx_ioctl()` handles `GET_INFO`, `GET_IRQ_INFO`, `SET_IRQS`, and `RESET`; `vfio_cdx_ioctl_feature()` handles `VFIO_DEVICE_FEATURE_BUS_MASTER`. `vfio_cdx_mmap()` decodes the high-bit region index and remaps page-aligned resources.

## Control Flow

Probe allocates a `struct vfio_cdx_device`, registers it as a VFIO group device, and stores it in driver data. Open allocates a region table sized by `cdx_dev->res_count`, derives secure mmap eligibility only for page-aligned address and size, marks read and optionally write permissions, resets the device, and attempts `cdx_clear_master()` to determine BME control support. Userspace obtains device info, region info, IRQ info, and then maps or controls regions. Close frees the region table, resets the device again, and cleans up IRQs.

## State and Persistence Behavior

The driver maintains per-open region metadata and per-device IRQ/BME support state in `struct vfio_cdx_device`. Device reset and bus-master feature operations affect hardware state. There is no persistent storage; state is reconstructed on open and destroyed on close/remove.

## Dependencies and Integration Points

It depends on the CDX bus, CDX reset/master APIs, VFIO core, iommufd physical helpers, VFIO IRQ validation, Linux MM APIs, and optional `intr.c` MSI support. The CDX driver uses `CDX_DEVICE_DRIVER_OVERRIDE(..., CDX_ID_F_VFIO_DRIVER_OVERRIDE)` and `driver_managed_dma = true`.

## Risks and Edge Cases

Open allocates regions and resets before checking bus-master support; if `cdx_clear_master()` fails, BME feature ioctls become unsupported but open still succeeds. Close does not clear `vdev->regions` after `kfree()`, though the open/close lifetime should make reuse impossible. MMAP checks permissions and page alignment but relies on the region metadata being valid for the current open. IRQ info reports only one IRQ index representing all MSI vectors.

## Test Signals

Test probe/remove, open reset, resource flag translation, page-aligned and unaligned mmap eligibility, read-only write denial, region offset encoding, IRQ info with zero/nonzero MSI count, set-IRQ validation paths, reset ioctl, bus-master set/clear feature success and unsupported cases, iommufd bind/attach, and close cleanup after partially configured IRQs.
