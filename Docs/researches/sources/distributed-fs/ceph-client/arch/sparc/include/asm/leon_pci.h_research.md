# sources/distributed-fs/ceph-client/arch/sparc/include/asm/leon_pci.h

## sources/distributed-fs/ceph-client/arch/sparc/include/asm/leon_pci.h

### Purpose
`sources/distributed-fs/ceph-client/arch/sparc/include/asm/leon_pci.h` declares LEON PCI initialization entry points. It is part of the SPARC architecture support imported in the Ceph client Linux source tree. Its direct consumers are low-level kernel architecture, bus, MMU, interrupt, PROM, and driver code; Ceph filesystem code depends on it only indirectly through a correctly functioning kernel platform layer.

### Important APIs, Types, And Functions
Source read size: 23 lines, 512 bytes. Primary surface: `leon_pci_init()` and `leon_pci_grpci1_init()`. Symbol scan highlights: `_ASM_LEON_PCI_H_`, `struct leon_pci_info`, `struct pci_ops`, `struct resource`, `leon_pci_init`.

### Control Flow
platform setup calls these helpers to initialize generic LEON PCI support and GRPCI1 host controller support. Because this is a header, most runtime behavior is selected by preprocessor branches or inlined/declared for implementation files; the executable flow is in the architecture, driver, or firmware-call code that includes it.

### State And Persistence
PCI bus/controller state is allocated by implementation files and PCI core. There is no userspace filesystem persistence in this file; persistent effects are kernel memory, firmware data, CPU registers, device registers, page tables, interrupt state, or ABI constants depending on the specific header.

### Dependencies
Direct includes: no direct include directives. Integration dependencies: LEON platform setup, PCI core, and GRPCI host controller code.

### Integration Points
The header integrates with SPARC boot, MMU/page-table setup, PROM/OpenFirmware discovery, interrupt delivery, DMA/IOMMU, PCI, LEON/AMBA platform support, LDOM/LDC, or parport paths according to its exported contract. For the distributed filesystem tree, the link is indirect but important: Ceph client networking, block I/O, page cache, and memory reclaim depend on these architecture contracts being correct for the kernel configuration.

### Risks
missing initialization leaves PCI devices undiscovered; host-controller variants must match hardware.

### Test Signals
LEON PCI boot/probe tests and PCI enumeration/resource assignment checks. Also require representative SPARC cross-builds and include-user compile coverage because many failures only appear in specific 32-bit, 64-bit, sun4v, LEON, or legacy SBus configurations.
