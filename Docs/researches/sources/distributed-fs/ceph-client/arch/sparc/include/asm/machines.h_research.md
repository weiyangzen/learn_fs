# sources/distributed-fs/ceph-client/arch/sparc/include/asm/machines.h

## sources/distributed-fs/ceph-client/arch/sparc/include/asm/machines.h

### Purpose
`sources/distributed-fs/ceph-client/arch/sparc/include/asm/machines.h` defines SPARC machine type identifiers and helper macros for sun4, sun4c, sun4m, sun4d, sun4e, and LEON-style systems. It is part of the SPARC architecture support imported in the Ceph client Linux source tree. Its direct consumers are low-level kernel architecture, bus, MMU, interrupt, PROM, and driver code; Ceph filesystem code depends on it only indirectly through a correctly functioning kernel platform layer.

### Important APIs, Types, And Functions
Source read size: 51 lines, 1540 bytes. Primary surface: `enum sparc_cpu`, `sparc_cpu_model`, and `ARCH_SUN4*`/`ARCH_LEON` predicates. Symbol scan highlights: `_SPARC_MACHINES_H`, `struct Sun_Machine_Models`, `SM_ARCH_MASK`, `M_LEON`, `SM_SUN4M`, `SM_SUN4M_OBP`, `SM_TYP_MASK`, `M_LEON3_SOC`, `SM_4M_SS60`, `SM_4M_SS50`, `SM_4M_SS40`.

### Control Flow
early platform detection sets `sparc_cpu_model`; architecture and driver code branches on the helper macros for model-specific setup. Because this is a header, most runtime behavior is selected by preprocessor branches or inlined/declared for implementation files; the executable flow is in the architecture, driver, or firmware-call code that includes it.

### State And Persistence
`sparc_cpu_model` persists the detected machine class. There is no userspace filesystem persistence in this file; persistent effects are kernel memory, firmware data, CPU registers, device registers, page tables, interrupt state, or ABI constants depending on the specific header.

### Dependencies
Direct includes: no direct include directives. Integration dependencies: PROM/IDPROM probing, platform setup, and model-specific architecture code.

### Integration Points
The header integrates with SPARC boot, MMU/page-table setup, PROM/OpenFirmware discovery, interrupt delivery, DMA/IOMMU, PCI, LEON/AMBA platform support, LDOM/LDC, or parport paths according to its exported contract. For the distributed filesystem tree, the link is indirect but important: Ceph client networking, block I/O, page cache, and memory reclaim depend on these architecture contracts being correct for the kernel configuration.

### Risks
misclassification selects wrong MMU, interrupt, or bus setup.

### Test Signals
boot logs across supported machine classes and unit-style checks of helper predicates. Also require representative SPARC cross-builds and include-user compile coverage because many failures only appear in specific 32-bit, 64-bit, sun4v, LEON, or legacy SBus configurations.
