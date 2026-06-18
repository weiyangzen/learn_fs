# sources/distributed-fs/ceph-client/arch/sparc/include/asm/lsu.h

## sources/distributed-fs/ceph-client/arch/sparc/include/asm/lsu.h

### Purpose
`sources/distributed-fs/ceph-client/arch/sparc/include/asm/lsu.h` defines SPARC64 Load Store Unit control-register bits for cache, MMU, parity, and interrupt-control behavior. It is part of the SPARC architecture support imported in the Ceph client Linux source tree. Its direct consumers are low-level kernel architecture, bus, MMU, interrupt, PROM, and driver code; Ceph filesystem code depends on it only indirectly through a correctly functioning kernel platform layer.

### Important APIs, Types, And Functions
Source read size: 20 lines, 1062 bytes. Primary surface: `LSU_CONTROL_*` bit masks such as `LSU_CONTROL_DC`, `LSU_CONTROL_IC`, `LSU_CONTROL_DM`, `LSU_CONTROL_IM`, parity, write-buffer, and P0 watchpoint flags. Symbol scan highlights: `_SPARC64_LSU_H`, `LSU_CONTROL_PM`, `LSU_CONTROL_VM`, `LSU_CONTROL_PR`, `LSU_CONTROL_PW`, `LSU_CONTROL_VR`, `LSU_CONTROL_VW`, `LSU_CONTROL_FM`, `LSU_CONTROL_DM`, `LSU_CONTROL_IM`, `LSU_CONTROL_DC`, `LSU_CONTROL_IC`.

### Control Flow
low-level CPU setup and trap/MMU code uses these bit definitions when reading or programming LSU control state. Because this is a header, most runtime behavior is selected by preprocessor branches or inlined/declared for implementation files; the executable flow is in the architecture, driver, or firmware-call code that includes it.

### State And Persistence
state lives in the CPU LSU control register. There is no userspace filesystem persistence in this file; persistent effects are kernel memory, firmware data, CPU registers, device registers, page tables, interrupt state, or ABI constants depending on the specific header.

### Dependencies
Direct includes: `<linux/const.h>`. Integration dependencies: SPARC64 CPU initialization, cache/MMU enable paths, and assembly register access.

### Integration Points
The header integrates with SPARC boot, MMU/page-table setup, PROM/OpenFirmware discovery, interrupt delivery, DMA/IOMMU, PCI, LEON/AMBA platform support, LDOM/LDC, or parport paths according to its exported contract. For the distributed filesystem tree, the link is indirect but important: Ceph client networking, block I/O, page cache, and memory reclaim depend on these architecture contracts being correct for the kernel configuration.

### Risks
wrong bit definitions can disable caches/MMUs or alter parity/watchpoint behavior unexpectedly.

### Test Signals
SPARC64 boot, cache/MMU enable tests, and register bit disassembly/source review. Also require representative SPARC cross-builds and include-user compile coverage because many failures only appear in specific 32-bit, 64-bit, sun4v, LEON, or legacy SBus configurations.
