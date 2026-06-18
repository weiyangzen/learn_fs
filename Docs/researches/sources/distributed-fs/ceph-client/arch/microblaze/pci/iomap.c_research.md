# sources/distributed-fs/ceph-client/arch/microblaze/pci/iomap.c

Purpose: implements MicroBlaze PCI I/O mapping helpers and controller tracking used by generic PCI unmap paths.

Important APIs and state: `hose_list`, `hose_spinlock`, exported `isa_io_base`, `pcibios_vaddr_is_ioport()`, `pci_proc_domain()`, and exported `pci_iounmap()`.

Control flow: `pcibios_vaddr_is_ioport()` scans registered PCI controllers under spinlock and checks whether a virtual address lies inside a hose I/O window. `pci_iounmap()` skips ISA and PCI I/O-port virtual ranges, otherwise calls generic `iounmap()`.

State and persistence: global controller list and ISA base persist for PCI subsystem lifetime.

Dependencies and integration: relies on platform PCI code populating `hose_list` and `io_base_virt`. Used by drivers calling `pci_iounmap()`.

Risks and test signals: bad hose resource sizes or missing list entries can iounmap I/O-port cookies incorrectly. Test PCI domain display, MMIO unmap, I/O port unmap skip, and multi-controller setups.
