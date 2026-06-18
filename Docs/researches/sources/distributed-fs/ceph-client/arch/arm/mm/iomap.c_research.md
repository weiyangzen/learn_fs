## sources/distributed-fs/ceph-client/arch/arm/mm/iomap.c

### Purpose
Provides ARM IO-port, VGA, PCI IO, and PCI memory mapping helpers.

### Important APIs, Types, And Functions
Exports `vga_base`, optional `ioport_map` and `ioport_unmap`, PCI globals `pcibios_min_io` and `pcibios_min_mem`, and `pci_iounmap`.

### Control Flow
`ioport_map` translates a port number through `__io` when available; unmap is a no-op for that static mapping model. `pci_iounmap` only calls `iounmap` for addresses inside the vmalloc range, leaving static or direct mappings alone.

### State, Dependencies, And Integration
State is global VGA/PCI minimum resource values. Depends on PCI, IO resource, io accessors, and optional `__io` platform macro. Integrates with generic PCI resource setup and driver IO-port mapping.

### Risks And Test Signals
Risks are incorrect static-vs-vmalloc unmap decisions, platform-specific `__io` translation mistakes, and bad PCI resource minima. Test PCI device probe/remove, IO port drivers, VGA access, and repeated `pci_iomap`/`pci_iounmap`.
