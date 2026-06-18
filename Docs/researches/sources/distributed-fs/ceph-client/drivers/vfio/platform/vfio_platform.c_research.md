<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/platform/vfio_platform.c -->
# sources/distributed-fs/ceph-client/drivers/vfio/platform/vfio_platform.c

## Purpose
This file is the generic platform-bus VFIO binder. It adapts Linux `platform_device` resources and IRQs to the shared VFIO platform base, allowing eligible platform devices to be assigned to userspace.

## Important APIs, types, and functions
`get_platform_resource()` calls `platform_get_mem_or_io()`, and `get_platform_irq()` calls `platform_get_irq_optional()`. `vfio_platform_init_dev()` fills the embedded `vfio_platform_device` with platform callbacks, name, flags, and the `reset_required` module parameter. `vfio_platform_ops` delegates VFIO operations to common platform code and physical iommufd binding helpers.

## Control flow
Probe allocates a VFIO platform device, registers it with VFIO group core, enables runtime PM, and stores driver data. Device initialization probes ACPI/OF metadata and reset availability through the common layer. Open/close/read/write/mmap/ioctl paths all flow through common platform exports. Removal unregisters, disables runtime PM, and puts the VFIO device.

## State and persistence behavior
The `reset_required` module parameter defaults to true and persists for the module lifetime. Per-device state is in memory in `vfio_platform_device`: resource callbacks, IRQ arrays, reset callback/module, compatible/HID, and runtime PM state. Regions and IRQs are allocated on open and freed on close.

## Dependencies and integration points
This file depends on the platform bus, VFIO core, runtime PM, shared VFIO platform base, and iommufd. It integrates with reset handlers via OF compatible strings or ACPI `_RST`.

## Risks and test signals
Main risks are assigning devices without reliable reset, resource ordering assumptions from userspace, and runtime PM imbalance on error paths. Test signals include probe/open failure without reset when required, `reset_required=0`, ACPI and OF devices, region and IRQ enumeration, runtime PM get/put, and iommufd attach/detach.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/platform/vfio_platform.c -->
