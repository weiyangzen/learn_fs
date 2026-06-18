# sources/distributed-fs/ceph-client/arch/sparc/lib/iomap.c

Purpose: Minimal SPARC I/O port mapping helpers.

Important APIs/functions: Exports `ioport_map`, `ioport_unmap`, and `pci_iounmap`.

Control flow: `ioport_map` converts an I/O port number to an `__iomem` address using SPARC I/O encoding. `ioport_unmap` and `pci_iounmap` are no-op unmap stubs for this architecture mapping model.

State and persistence: No persistent state or allocation.

Dependencies/integration: Includes `linux/pci.h`, `linux/module.h`, and `asm/io.h`; used by generic PCI/I/O code.

Risks/test signals: Address translation must match SPARC I/O accessor expectations. Test drivers using port I/O, mapping/unmapping smoke tests, and sparse address annotations.
