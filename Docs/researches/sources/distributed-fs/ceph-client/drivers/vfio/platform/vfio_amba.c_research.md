<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/platform/vfio_amba.c -->
# sources/distributed-fs/ceph-client/drivers/vfio/platform/vfio_amba.c

## Purpose
This deprecated driver binds ARM AMBA devices into VFIO using the shared VFIO platform base. It is a bus-specific wrapper that provides AMBA resource and IRQ discovery and delegates device operations to `vfio_platform_common.c`.

## Important APIs, types, and functions
`get_amba_resource()` exposes only `adev->res` as region 0. `get_amba_irq()` returns AMBA IRQ slots, translating zero to `-ENXIO`. `vfio_amba_init_dev()` fills `vfio_platform_device` fields including name, flags, callbacks, and `reset_required = false`. `vfio_amba_ops` supplies VFIO callbacks for open, close, ioctl, region info, read, write, mmap, and iommufd physical binding.

## Control flow
Probe logs a deprecation warning, allocates a VFIO platform device with `vfio_alloc_device`, registers it as a VFIO group device, enables runtime PM, and stores driver data. Removal unregisters the group device, disables runtime PM, and drops the VFIO device reference. Init and release callbacks set up and tear down common platform state.

## State and persistence behavior
Per-device state lives in `struct vfio_platform_device`: generated name, AMBA opaque pointer, callbacks, IRQ/resource arrays initialized on open, and reset metadata. Runtime PM is enabled for the device while bound. No disk persistence exists.

## Dependencies and integration points
The file depends on the AMBA bus, VFIO core, VFIO platform base exports, runtime PM, and iommufd physical attach operations. Its `driver_managed_dma = true` flag integrates with DMA ownership expectations for VFIO.

## Risks and test signals
Risks include deprecated status, lack of required reset by default, only one AMBA memory resource being exposed, and unset IRQ semantics. Test signals include AMBA probe/remove, VFIO device info flags, region 0 access, IRQ enumeration, runtime PM balancing, and iommufd bind/attach calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/platform/vfio_amba.c -->
