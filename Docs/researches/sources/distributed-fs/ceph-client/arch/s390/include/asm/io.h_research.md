# sources/distributed-fs/ceph-client/arch/s390/include/asm/io.h

Purpose: This header wires s390 generic I/O memory APIs to s390 physical mapping and zPCI instruction-backed MMIO helpers.

Important APIs/types/functions: `xlate_dev_mem_ptr()`, `unxlate_dev_mem_ptr()`, `ioremap_prot`, `ioremap_wc`, no-op `ioport_map/unmap`, PCI-specific `pci_iomap` overrides, `memcpy_fromio/toio`, `memset_io`, `mmiowb`, raw read/write aliases, and `__iowrite32_copy`/`__iowrite64_copy` are the key interfaces.

Control flow: Non-port I/O either maps device memory through architecture mapping helpers or, for PCI, uses s390 private pci_iomap cookies because BAR spaces are not disjoint. MMIO reads/writes route through zPCI load/store instructions and larger copy helpers.

State and persistence: The header stores no state; mapping cookies and zPCI iomap tables persist in the PCI implementation. It defines policy that legacy port I/O has no address space (`IO_SPACE_LIMIT 0`).

Dependencies and integration points: It depends on `page.h`, `pgtable.h`, `pci_io.h`, and `asm-generic/io.h`, integrating Linux MMIO abstractions with zPCI BAR mapping and write-combining protection helpers.

Risks and test signals: Treating s390 PCI cookies like linear ioremap addresses can address the wrong BAR. Tests should include pci_iomap/iounmap, raw read/write sizes, memcpy_to/fromio crossing boundaries, write-combine mappings, and non-PCI builds.
