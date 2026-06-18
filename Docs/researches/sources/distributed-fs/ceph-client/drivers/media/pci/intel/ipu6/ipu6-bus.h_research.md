# sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-bus.h

## Purpose
This header defines the IPU6 auxiliary device abstraction shared by the PCI core, buttress, DMA, firmware, and ISYS/PSYS auxiliary drivers.

## Important APIs, types, and functions
`struct ipu6_bus_device` embeds `struct auxiliary_device` and stores auxiliary driver metadata, list linkage, platform data, MMU, parent `ipu6_device`, buttress control, firmware image, firmware scatterlist, and firmware package directory DMA state. `struct ipu6_auxdrv_data` provides top-half and threaded IRQ callbacks plus a flag for threaded wakeup. Helper macros convert devices and auxiliary devices to `ipu6_bus_device` and access driver data. The public functions are `ipu6_bus_initialize_device()`, `ipu6_bus_add_device()`, and `ipu6_bus_del_devices()`.

## Control flow and integration points
The header is the contract between the PCI parent and auxiliary subsystem drivers. Buttress IRQ dispatch uses `auxdrv_data` callbacks. Firmware authentication and CPD package directory logic use the firmware and package fields. DMA helpers use `adev->mmu` and the auxiliary device for logging and ownership.

## State, persistence, and dependencies
The structure persists for the lifetime of each auxiliary child and is released by the auxiliary device release callback. It depends on Linux auxiliary bus, device, IRQ, list, scatterlist, and type definitions plus forward-declared IPU6-specific types.

## Risks and test signals
Risks are lifetime mismatches between embedded auxiliary device and IPU6-specific resources, stale `auxdrv_data` during IRQ dispatch, and missing initialization of firmware/MMU/package fields before consumers run. Test signals include probe/remove with KASAN, IRQs during bind/unbind, firmware load/authentication, DMA allocation through `adev->mmu`, and module unload.
