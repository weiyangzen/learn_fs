# sources/distributed-fs/ceph-client/include/linux/bcma/bcma_driver_pci.h

## Purpose
Defines BCMA PCI/PCIe core registers, SERDES/MDIO constants, host-mode structures, PCI-core state, register access macros, and optional host-mode callbacks.

## Important APIs, types, and functions
- Register constants cover PCI control/arbiter/interrupt/mailbox/GPIO, backplane-to-PCI translation, config access, MDIO/SERDES, PCIe indirect registers, SPROM, PLP/DLLP diagnostics, and root capability bits.
- `struct bcma_drv_pci_host` exists under host-mode config and owns config-space lock, PCI controller/ops, and IO/memory resources.
- `struct bcma_drv_pci` stores core pointer, setup flags, hostmode flag, and optional host controller.
- Access macros `pcicore_read16/32()` and write variants wrap BCMA core access.
- Optional APIs include `bcma_core_pci_power_save()`, `bcma_core_pci_pcibios_map_irq()`, and `bcma_core_pci_plat_dev_init()`, with disabled stubs.

## Control flow and state
BCMA PCI setup programs translation windows, interrupt masks, SERDES/MDIO, and optionally host-mode PCI controller resources. Endpoint code can power-save the PCI core. Host-mode PCI config access is serialized by `cfgspace_lock`.

## State and persistence behavior
State is live PCI/PCIe core register state plus runtime setup flags. SPROM shadow registers mirror persistent board configuration but writes require explicit enable/control sequences.

## Dependencies and integration points
Depends on kernel PCI types, resources, spinlocks, and BCMA core accessors. Integrated by BCMA PCI host/endpoint support, PCI IRQ mapping, SPROM handling, and wireless/SoC devices behind BCMA.

## Risks
The register map is revision-sensitive. MDIO field shifts differ for old revisions. Translation window mistakes can corrupt bus addressing. Host-mode config accesses must be locked and resource ranges must match SoC address maps.

## Test signals
Test endpoint and host-mode builds, PCI enumeration, config-space access, IRQ mapping, power-save transitions, SERDES link status, SPROM reads, and legacy revision MDIO paths.
