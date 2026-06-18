<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/pci.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/asm/pci.h

**Purpose:** Declares Alpha's PCI controller abstraction and legacy PCI interfaces. It represents multi-hose systems, dense/sparse I/O windows, DMA arenas, and domain numbering.

**Important APIs/types/functions:** `struct pci_controller`, `pcibios_assign_all_busses`, `PCIBIOS_MIN_IO`, `PCIBIOS_MIN_MEM`, `pci_domain_nr`, `pci_proc_domain`, IOBASE constants, `isa_bridge`, and legacy read/write/mmap helpers.

**Control flow:** PCI core code obtains per-bus hose data from `bus->sysdata`, derives PCI domains from `hose->index`, and uses machine-vector minimum I/O and memory addresses for resource assignment.

**State and persistence behavior:** Each hose carries resource pointers, sparse/dense base addresses, config-space base, optional SG arenas, a linked-list node, index, and system-specific private data. This state lives for the booted kernel.

**Dependencies and integration points:** Depends on Linux PCI, DMA, scatterlist, spinlock, and `asm/machvec.h`. Populated by Alpha core-logic files and consumed by generic PCI enumeration, sysfs, legacy mmap, and DMA mapping.

**Risks:** Bad hose ranges or domain numbering can break resource allocation on multi-controller systems. Dense/sparse base mistakes expose wrong physical I/O windows to user space and drivers.

**Test signals:** Boot PCI enumeration on single-hose and multi-hose Alpha machines, verify `/proc/bus/pci` domain behavior, legacy I/O mmap, DMA arena setup, and resource assignment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/pci.h -->
