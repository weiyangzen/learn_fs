# sources/distributed-fs/ceph-client/drivers/ssb/b43_pci_bridge.c

## Purpose
Tiny PCI ID bridge that lets Broadcom 43xx PCI wireless devices be claimed as SSB PCI hosts for b43-era hardware.

## Important APIs, Types, and Functions
Defines `b43_pci_bridge_tbl`, a PCI device ID table for many Broadcom 43xx IDs. Exposes `b43_pci_ssb_bridge_init` and `b43_pci_ssb_bridge_exit`, which call `ssb_pcihost_register`/`ssb_pcihost_unregister` with `b43_pci_bridge_driver`.

## Control Flow
SSB module init invokes bridge init. PCI core matches listed IDs to the driver, and the SSB PCI host wrapper performs the real SSB bus registration. Exit unregisters the PCI driver.

## State and Persistence
No private runtime state; PCI driver registration is the only state. Device ownership is managed by the PCI and SSB host layers.

## Dependencies and Integration Points
Depends on PCI, `ssb_private.h`, and SSB PCI host support. It is not a standalone module despite representing a PCI driver.

## Risks
ID table omissions block SSB discovery for supported wireless cards. Because the driver has no local probe/remove, correctness depends entirely on `ssb_pcihost_register` attaching callbacks. The decimal-looking `43222` device ID is intentional elsewhere in SSB code but is easy to misread.

## Test Signals
PCI modalias table should include listed IDs; on matching hardware, `ssb_pcihost_register` should discover the SSB bus and b43 devices. Init failure should be logged but not prevent the SSB core from loading.
