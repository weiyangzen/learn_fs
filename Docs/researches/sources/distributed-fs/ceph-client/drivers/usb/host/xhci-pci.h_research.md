# sources/distributed-fs/ceph-client/drivers/usb/host/xhci-pci.h

## Purpose
Declares the small shared interface between the generic xHCI PCI driver and the Renesas PCI firmware-loading wrapper.

## Important APIs, Types, And Functions
The header declares `xhci_pci_common_probe(struct pci_dev *dev, const struct pci_device_id *id)` and `xhci_pci_remove(struct pci_dev *dev)`. It relies on included context for `struct pci_dev` and `struct pci_device_id`.

## Control Flow
The header has no execution. It allows `xhci-pci-renesas.c` to perform Renesas firmware work, then enter the same common probe path as generic PCI xHCI, and to use the same remove callback.

## State And Persistence
No state is defined. Ownership and lifetime belong to the implementations in `xhci-pci.c` and the caller's PCI driver.

## Dependencies And Integration Points
This is a private compile-time boundary within the xHCI host directory. The implementation exports the functions in the `xhci` namespace, so module builds also depend on namespace import in the Renesas driver.

## Risks And Test Signals
Risks include declaration drift, missing PCI type declarations in include order, and namespace/export mismatches for modular builds. Test signals are successful builds with generic PCI xHCI alone and with `CONFIG_USB_XHCI_PCI_RENESAS`, plus module load/unload of both drivers.
