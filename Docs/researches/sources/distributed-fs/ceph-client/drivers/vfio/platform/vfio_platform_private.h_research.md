<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/platform/vfio_platform_private.h -->
# sources/distributed-fs/ceph-client/drivers/vfio/platform/vfio_platform_private.h

## Purpose
This private header defines the shared data model and prototypes for VFIO platform and AMBA drivers, including region indexing, IRQ state, platform device state, and reset handler registration.

## Important APIs, types, and functions
Key macros are `VFIO_PLATFORM_OFFSET_SHIFT`, `VFIO_PLATFORM_OFFSET_MASK`, `VFIO_PLATFORM_OFFSET_TO_INDEX`, and `VFIO_PLATFORM_INDEX_TO_OFFSET`. Key structs are `vfio_platform_irq`, `vfio_platform_region`, `vfio_platform_device`, and `vfio_platform_reset_node`. The header declares common lifecycle, ioctl, read/write/mmap, IRQ, and reset registry functions. `module_vfio_reset_handler()` creates module init/exit functions plus `MODULE_ALIAS("vfio-reset:<compat>")`.

## Control flow
Bus-specific binders fill `vfio_platform_device` callbacks and flags, then common code uses these fields to discover resources, interrupts, firmware identity, and reset support. Reset modules instantiate a static reset node and register it on module init.

## State and persistence behavior
The structs describe all important in-memory state: regions with physical addresses and cached `ioaddr`, IRQ eventfd state, reset module ownership, compatible/HID strings, and bus-specific opaque pointers. There is no persistent storage.

## Dependencies and integration points
The header depends on Linux VFIO and interrupt types. It integrates platform C files, AMBA C files, reset modules, and VFIO core uAPI behavior.

## Risks and test signals
ABI-adjacent risk lies in offset encoding: changing the 40-bit index shift would break userspace region offsets. Reset registration macros depend on unique reset function names. Test signals include compile coverage for all platform modules, region offset round trips, reset module autoload aliases, and lockdep coverage around IRQ state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/platform/vfio_platform_private.h -->
