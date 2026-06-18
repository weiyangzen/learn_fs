# sources/distributed-fs/ceph-client/arch/x86/include/asm/probe_roms.h

Purpose: declares x86 PCI BIOS ROM mapping helpers used by ROM probing code.

Important APIs, types, and functions: forward declares `struct pci_dev` and exports `pci_map_biosrom(struct pci_dev *pdev)`, `pci_unmap_biosrom(void __iomem *rom)`, and `pci_biosrom_size(struct pci_dev *pdev)`.

Control flow: no implementation is present. Callers map a device BIOS ROM, inspect or copy it, query its size, and then unmap it.

State and persistence: mappings are temporary kernel I/O mappings of device ROM address space. The header owns no state.

Dependencies and integration points: used by x86 ROM probing and PCI device firmware/option-ROM paths. It depends on PCI device metadata and ioremap/unmap implementation elsewhere.

Risks: ROM windows can be disabled, shared, or require decode enabling. Incorrect mapping size or missing unmap can leak mappings or access invalid firmware memory.

Test signals: option ROM reads on PCI devices, size detection, map/unmap leak checks, disabled ROM BAR handling, and systems with legacy BIOS extension ROMs.
