# sources/distributed-fs/ceph-client/drivers/pci/pci-stub.c

## Purpose
Implements a generic PCI stub driver used to reserve devices, commonly for VM assignment. It binds only dynamic IDs supplied through module parameters or the PCI driver's `new_id` sysfs interface.

## APIs, Types, And Functions
Defines module parameter `ids`, `pci_stub_probe()`, `stub_driver`, `pci_stub_init()`, and `pci_stub_exit()`. The driver has no static ID table and sets `driver_managed_dma = true`.

## Control Flow
Initialization registers the PCI driver, parses comma-separated `vendor:device[:subvendor[:subdevice[:class[:class_mask]]]]` strings from the `ids` module parameter, validates at least vendor/device fields, and calls `pci_add_dynid()` for each valid entry. Probe only logs a successful claim. Exit unregisters the driver, which frees dynamic IDs through PCI driver-core cleanup.

## State And Persistence
Runtime state is in the PCI driver's dynamic ID list and device binding relationships. The boot/module parameter is init data and is discarded after initialization. There is no persistent storage.

## Dependencies And Integration
Depends on PCI driver registration, dynamic ID support in `pci-driver.c`, module parameter parsing, and sysfs bind/unbind flows. It is often used with VFIO/KVM workflows that require a device to be detached from its normal driver.

## Risks And Test Signals
Risks include malformed ID parsing, dynamic ID addition failures after partial registration, binding devices that should remain managed by real drivers, and DMA/IOMMU expectations due to `driver_managed_dma`. Test signals include module parameter parsing with multiple IDs, sysfs `new_id`/bind/unbind flows, invalid ID warnings, driver unregister cleanup, and VM assignment smoke tests.
