# sources/distributed-fs/ceph-client/arch/sparc/include/asm/pbm.h

## sources/distributed-fs/ceph-client/arch/sparc/include/asm/pbm.h

### Purpose
`sources/distributed-fs/ceph-client/arch/sparc/include/asm/pbm.h` defines SPARC PCI Bus Module software state compatible with SPARC64 PBM abstractions for SPARC PCIC/PCI code. It is part of the SPARC architecture support imported in the Ceph client Linux source tree. Its direct consumers are low-level kernel architecture, bus, MMU, interrupt, PROM, and driver code; Ceph filesystem code depends on it only indirectly through a correctly functioning kernel platform layer.

### Important APIs, Types, And Functions
Source read size: 48 lines, 1505 bytes. Primary surface: `struct linux_pbm_info` and `struct pcidev_cookie`. Symbol scan highlights: `__SPARC_PBM_H`, `struct linux_pbm_info`, `struct pci_bus`, `struct pcidev_cookie`, `struct device_node`.

### Control Flow
PCI probing creates a PBM record from PROM data, attaches the Linux PCI bus, and stores per-device cookies that point back to the PBM and PROM node. Because this is a header, most runtime behavior is selected by preprocessor branches or inlined/declared for implementation files; the executable flow is in the architecture, driver, or firmware-call code that includes it.

### State And Persistence
PBM and per-device cookies persist for PCI bus/device lifetime through PCI `sysdata` and driver data. There is no userspace filesystem persistence in this file; persistent effects are kernel memory, firmware data, CPU registers, device registers, page tables, interrupt state, or ABI constants depending on the specific header.

### Dependencies
Direct includes: `<linux/pci.h>`, `<asm/oplib.h>`, `<asm/prom.h>`. Integration dependencies: `linux/pci.h`, `asm/oplib.h`, `asm/prom.h`, PCI core, PROM device tree, and SPARC PCIC code.

### Integration Points
The header integrates with SPARC boot, MMU/page-table setup, PROM/OpenFirmware discovery, interrupt delivery, DMA/IOMMU, PCI, LEON/AMBA platform support, LDOM/LDC, or parport paths according to its exported contract. For the distributed filesystem tree, the link is indirect but important: Ceph client networking, block I/O, page cache, and memory reclaim depend on these architecture contracts being correct for the kernel configuration.

### Risks
bad PROM node association makes OBP-aware drivers use wrong firmware properties; bus numbering assumptions can break multi-bus probing.

### Test Signals
SPARC PCI enumeration, sysdata cookie inspection, OBP-aware PCI driver probe tests, and resource assignment validation. Also require representative SPARC cross-builds and include-user compile coverage because many failures only appear in specific 32-bit, 64-bit, sun4v, LEON, or legacy SBus configurations.
