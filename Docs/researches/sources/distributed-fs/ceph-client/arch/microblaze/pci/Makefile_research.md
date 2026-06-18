# sources/distributed-fs/ceph-client/arch/microblaze/pci/Makefile

Purpose: selects MicroBlaze PCI iomap support when PCI is enabled.

Important build rules and state: `obj-$(CONFIG_PCI) += iomap.o`.

Control flow: build-time only.

State and persistence: determines whether MicroBlaze PCI I/O unmap helpers and controller list state are linked.

Dependencies and integration: used with architecture PCI setup from `setup_arch()` and generic PCI code.

Risks and test signals: PCI builds without `iomap.o` would lack `pci_iounmap` behavior. Test `CONFIG_PCI=y/n` build matrix.
