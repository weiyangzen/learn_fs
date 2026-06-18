# sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-pci.h

## Purpose
This header defines the private contract between the generic SDHCI PCI driver and vendor-specific PCI fixup files. It centralizes PCI device IDs, table-construction macros, slot/chip data structures, fixup callbacks, and exported fixup declarations for Arasan, Synopsys, O2Micro, and Genesys devices.

## Important APIs, Types, And Functions
`struct sdhci_pci_fixes` is the central extension point. It carries SDHCI `quirks`, `quirks2`, runtime-PM policy, optional chip and slot probe callbacks, host add/remove callbacks, slot remove hooks, sleep/runtime PM callbacks, a replacement `sdhci_ops` table, optional CD GPIO override DMI table, and per-slot private size. `struct sdhci_pci_slot` binds a `struct sdhci_host` to its owning `struct sdhci_pci_chip`, card-detect override data, optional hardware reset callback, and aligned private storage. `struct sdhci_pci_chip` tracks the PCI device, aggregate quirks, PM flags, selected fixups, slot count, and slot pointers. `sdhci_pci_priv()` returns the vendor-private tail memory. Declarations expose `sdhci_pci_uhs2_add_host()`, `sdhci_pci_uhs2_remove_host()`, `sdhci_pci_resume_host()`, and `sdhci_pci_enable_dma()`.

## Control Flow
The generic PCI driver matches devices using `SDHCI_PCI_DEVICE`, `SDHCI_PCI_SUBDEVICE`, or `SDHCI_PCI_DEVICE_CLASS`. Those macros store a pointer to a `sdhci_<cfg>` fixup object in `driver_data`. During probe, the core allocates a chip and slots, applies chip-level callbacks, attaches per-slot private memory sized by `priv_size`, applies slot callbacks, and invokes custom add/remove/PM hooks when provided.

## State And Persistence
The structures in this header define all persistent PCI SDHCI driver state across probe, runtime, and PM transitions. Vendor files mutate chip and slot fields indirectly through these structures, and the generic PCI driver uses them to replay resume, remove dead hosts, and track runtime retuning flags.

## Dependencies And Integration Points
It depends on PCI class/vendor/device constants, `struct sdhci_host`, `struct sdhci_ops`, DMI declarations, and optional PM config. Every `sdhci-pci-*` vendor file includes this header, and the central `sdhci-pci.c` implementation consumes the declarations and structures.

## Risks
The callback structure is broad and hardware-specific; misconfigured fixup tables can route a device to the wrong ops or omit required private storage. `private[]` alignment means callers must use `sdhci_pci_priv()` rather than assuming fixed layout. PM callback availability changes with kernel config, so code must remain correct with and without `CONFIG_PM`/`CONFIG_PM_SLEEP`.

## Test Signals
Build coverage should include PCI vendor fixup files with different PM configs. Runtime signals are correct device-table binding, expected quirk propagation, per-slot private state availability, UHS-II add/remove paths for relevant devices, and DMA enable behavior through `sdhci_pci_enable_dma()`.
