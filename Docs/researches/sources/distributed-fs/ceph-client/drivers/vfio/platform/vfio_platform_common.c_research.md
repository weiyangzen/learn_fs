<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/platform/vfio_platform_common.c -->
# sources/distributed-fs/ceph-client/drivers/vfio/platform/vfio_platform_common.c

## Purpose
This shared base implements most VFIO platform device behavior: firmware probing, reset-handler lookup and invocation, region discovery, IRQ initialization, VFIO ioctls, MMIO read/write, mmap, and reset handler registry management.

## Important APIs, types, and functions
Exported APIs include `vfio_platform_init_common`, `vfio_platform_release_common`, `vfio_platform_open_device`, `vfio_platform_close_device`, `vfio_platform_ioctl`, `vfio_platform_ioctl_get_region_info`, `vfio_platform_read`, `vfio_platform_write`, `vfio_platform_mmap`, `__vfio_platform_register_reset`, and `vfio_platform_unregister_reset`. Internally, `reset_list` and `driver_lock` manage registered OF-compatible reset handlers. `VFIO_PLATFORM_INDEX_TO_OFFSET` and `VFIO_PLATFORM_OFFSET_TO_INDEX` encode region indexes into VFIO file offsets.

## Control flow
Device init tries ACPI first and then OF compatible probing. It initializes the IRQ gate mutex and obtains a reset path, either ACPI `_RST` or OF reset handler module autoloaded through `vfio-reset:<compat>`. Open initializes regions, initializes IRQs, resumes runtime PM, and calls reset; failure unwinds IRQs, regions, and PM. Close calls reset, runtime-PM put, region cleanup, and IRQ cleanup. Ioctl handles device info, IRQ info, `VFIO_DEVICE_SET_IRQS`, and `VFIO_DEVICE_RESET`, while region info is served through the VFIO core region callback.

## State and persistence behavior
Per-open state includes allocated `regions`, `irqs`, cached `ioaddr` mappings, runtime PM usage, and eventfd IRQ state from the IRQ layer. Reset module references are held after lookup and released during common release. Region MMIO mappings are lazily ioremapped during reset or read/write and unmapped on close. No disk persistence exists.

## Dependencies and integration points
The file depends on ACPI, device properties, IOMMU/VFIO uAPI structs, runtime PM, module autoloading, and the platform IRQ module. It integrates with bus binders through resource/IRQ callbacks and with reset modules through `vfio_platform_reset_node`.

## Risks and test signals
Security hinges on reset reliability, page-aligned mmap checks, and correct resource flags. Risks include PIO resources being exposed but unimplemented, reset handlers returning success after partial hardware failure, and stale module references if registration changes. Test signals include ACPI `_RST`, OF reset autoload, read/write width splitting, mmap bounds and permission failures, IRQ ioctl validation, and close-time reset warning behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/platform/vfio_platform_common.c -->
