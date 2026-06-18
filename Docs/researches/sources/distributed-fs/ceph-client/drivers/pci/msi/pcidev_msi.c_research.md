# sources/distributed-fs/ceph-client/drivers/pci/msi/pcidev_msi.c

## Purpose
Performs unconditional MSI and MSI-X capability discovery during PCI device initialization and disables any firmware-left-enabled MSI/MSI-X state to prevent interrupt storms before drivers take ownership.

## APIs, Types, And Functions
Provides `pci_msi_init()` and `pci_msix_init()`. These set `dev->msi_cap` and `dev->msix_cap` from PCI capability lookup, read capability control registers, clear enable bits if needed, and set a 32-bit MSI address mask for non-64-bit MSI devices.

## Control Flow
Each initializer searches for its capability. If absent, it returns. If present and already enabled, it writes the control register with the enable bit cleared. MSI additionally inspects the 64-bit flag and constrains `dev->msi_addr_mask` for 32-bit-only devices.

## State And Persistence
State is limited to `struct pci_dev` capability offsets and `msi_addr_mask`; hardware control bits are reset in PCI config space. There is no filesystem persistence.

## Dependencies And Integration
Depends on PCI config-space helpers and register constants from `../pci.h`. Enumeration code calls these before drivers request IRQ vectors, and `msi.c` later relies on initialized `msi_cap`, `msix_cap`, and address-mask fields.

## Risks And Test Signals
Risks include firmware leaving MSI/MSI-X enabled, broken devices requiring careful config writes, and wrong address mask setup for 32-bit MSI devices. Test signals include enumeration of devices with MSI already enabled, MSI-X already enabled, no capability, and 32-bit MSI-only capability.
