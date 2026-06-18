# sources/distributed-fs/ceph-client/arch/sparc/include/asm/mbus.h

## sources/distributed-fs/ceph-client/arch/sparc/include/asm/mbus.h

### Purpose
`sources/distributed-fs/ceph-client/arch/sparc/include/asm/mbus.h` defines MBUS module-id decoding, cache-controller constants, and helper macros for SPARC32 MBus-based systems. It is part of the SPARC architecture support imported in the Ceph client Linux source tree. Its direct consumers are low-level kernel architecture, bus, MMU, interrupt, PROM, and driver code; Ceph filesystem code depends on it only indirectly through a correctly functioning kernel platform layer.

### Important APIs, Types, And Functions
Source read size: 97 lines, 2996 bytes. Primary surface: `struct mbus_device`, `MBUS_*` manufacturer/module macros, `mbus_module_*` predicates, `mbus_read_*`, and cache-control bits. Symbol scan highlights: `_SPARC_MBUS_H`, `enum mbus_module`, `HWBUG_COPYBACK_BROKEN`, `HWBUG_ASIFLUSH_BROKEN`, `HWBUG_VACFLUSH_BITROT`, `HWBUG_KERN_ACCBROKEN`, `HWBUG_KERN_CBITBROKEN`, `HWBUG_MODIFIED_BITROT`, `HWBUG_PC_BADFAULT_ADDR`, `HWBUG_SUPERSCALAR_BAD`, `HWBUG_PACINIT_BITROT`, `MBUS_VIKING`, `MBUS_LSI`, `MBUS_ROSS`, `MBUS_FMI`, `ROSS_604_REV_CDE`, `ROSS_604_REV_F`, `ROSS_605`, `ROSS_605_REV_B`, `VIKING_REV_12`, `VIKING_REV_2`, `VIKING_REV_30`, `VIKING_REV_35`, `LSI_L64815`, and 6 more.

### Control Flow
CPU/bus discovery reads module IDs, decodes vendor and implementation, and selects cache/MMU workarounds or controller setup. Because this is a header, most runtime behavior is selected by preprocessor branches or inlined/declared for implementation files; the executable flow is in the architecture, driver, or firmware-call code that includes it.

### State And Persistence
module IDs and cache controller registers are hardware state; decoded values influence boot-time configuration. There is no userspace filesystem persistence in this file; persistent effects are kernel memory, firmware data, CPU registers, device registers, page tables, interrupt state, or ABI constants depending on the specific header.

### Dependencies
Direct includes: `<asm/ross.h>    /* HyperSparc stuff */`, `<asm/viking.h>  /* Ugh, bug city... */`. Integration dependencies: SPARC32 CPU probing, MBus register access, cache/MXCC/Viking/TurboSparc handling, and platform setup.

### Integration Points
The header integrates with SPARC boot, MMU/page-table setup, PROM/OpenFirmware discovery, interrupt delivery, DMA/IOMMU, PCI, LEON/AMBA platform support, LDOM/LDC, or parport paths according to its exported contract. For the distributed filesystem tree, the link is indirect but important: Ceph client networking, block I/O, page cache, and memory reclaim depend on these architecture contracts being correct for the kernel configuration.

### Risks
wrong module decoding can skip necessary CPU/cache errata handling.

### Test Signals
SPARC32 boot on sun4m variants, module-id logs, cache controller tests, and cross-build coverage. Also require representative SPARC cross-builds and include-user compile coverage because many failures only appear in specific 32-bit, 64-bit, sun4v, LEON, or legacy SBus configurations.
