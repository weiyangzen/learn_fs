# sources/distributed-fs/ceph-client/drivers/pci/pci-bridge-emul.h

## Purpose
Declares the data model and API for the PCI bridge configuration-space emulator. It describes the emulated base bridge header, PCIe capability header, callback operations, feature flags, and read/write entry points.

## APIs, Types, And Functions
Defines `struct pci_bridge_emul_conf`, `struct pci_bridge_emul_pcie_conf`, `pci_bridge_emul_read_status_t`, `struct pci_bridge_emul_ops`, and `struct pci_bridge_emul`. Public functions are `pci_bridge_emul_init()`, `pci_bridge_emul_cleanup()`, `pci_bridge_emul_conf_read()`, and `pci_bridge_emul_conf_write()`. Flags include `PCI_BRIDGE_EMUL_NO_PREFMEM_FORWARD` and `PCI_BRIDGE_EMUL_NO_IO_FORWARD`.

## Control Flow
The header establishes the callback contract: read callbacks may handle a register or let common emulation read from memory; write callbacks receive old, new, and mask values after common behavior filtering. The implementation uses the declared structs as byte-accurate config-space backing storage.

## State And Persistence
`struct pci_bridge_emul` stores emulated config state, behavior-table pointers allocated at init, optional capability locations, subsystem IDs, callback ops, and driver private data. State is caller-owned and memory-only.

## Dependencies And Integration
Depends on kernel types and PCI register layout assumptions. It is consumed by host controller drivers and implemented by `pci-bridge-emul.c`.

## Risks And Test Signals
Risks include structure layout drift from PCI config offsets, wrong callback interpretation, uninitialized capability offsets, and forgetting cleanup for allocated behavior tables. Test signals include compile-time struct size checks, host driver config-space tests, capability layout validation, and cleanup leak checks.
