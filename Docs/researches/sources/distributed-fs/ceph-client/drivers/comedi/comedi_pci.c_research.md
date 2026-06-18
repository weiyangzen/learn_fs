# sources/distributed-fs/ceph-client/drivers/comedi/comedi_pci.c

## Purpose

`comedi_pci.c` is the COMEDI PCI bus helper module. It provides common helpers for PCI-backed COMEDI drivers: PCI lookup, enable/disable, generic detach cleanup, auto-config/unconfig wrappers, and combined COMEDI/PCI registration.

## APIs And Flow

`comedi_to_pci_dev()` converts `dev->hw_dev` to `struct pci_dev`. `comedi_pci_enable()` enables the device, requests BAR regions, and sets `dev->ioenabled`; `comedi_pci_disable()` reverses that. `comedi_pci_detach()` frees IRQ, unmaps `dev->mmio`, and disables PCI. `comedi_pci_auto_config()`/`auto_unconfig()` bridge PCI probe/remove to COMEDI auto attach/detach. `comedi_pci_driver_register()` registers the COMEDI driver first and unwinds it if PCI registration fails; unregister reverses the order.

## State, Dependencies, Risks, Tests

The helper modifies `dev->ioenabled`, `dev->irq`, and `dev->mmio`; no private state exists. Dependencies are PCI APIs, interrupts, module exports, and `linux/comedi/comedi_pci.h`. Risks include nested enable/disable misuse, stale `ioenabled`, incomplete cleanup for drivers with extra resources, registration unwind mistakes, and non-PCI `hw_dev`. Test probe/remove, failed region request, failed PCI registration, manual detach before remove, and repeated module load/unload.
