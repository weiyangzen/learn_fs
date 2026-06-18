# sources/distributed-fs/ceph-client/arch/sparc/include/asm/vaddrs.h

Purpose: SPARC32 virtual-address layout header for SRMMU nocache area, fixed mappings, IO space, debugger/PROM ranges, and DVMA windows.

Important APIs/types/functions: macros/constants `_SPARC_VADDRS_H`, `SRMMU_MAXMEM`, `SRMMU_NOCACHE_VADDR`, `SRMMU_MIN_NOCACHE_PAGES`, `SRMMU_MAX_NOCACHE_PAGES`, `SRMMU_NOCACHE_ALCRATIO`, `FIXADDR_TOP`, `FIXADDR_SIZE`, `FIXADDR_START`, `__fix_to_virt`, `SUN4M_IOBASE_VADDR`, `IOBASE_VADDR`, `IOBASE_END`, `KADB_DEBUGGER_BEGVM`, `KADB_DEBUGGER_ENDVM`, `DEBUG_FIRSTVADDR`, `DEBUG_LASTVADDR`, `LINUX_OPPROM_BEGVM`, plus 3 more.

Control flow: The file is driven by preprocessor gates such as `_SPARC_VADDRS_H`, `__ASSEMBLER__`, `CONFIG_HIGHMEM`. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into memory-management paths rather than through standalone functions.

State and persistence behavior: State is compile-time virtual address partitioning consumed by MMU setup, IO mapping, and DVMA code; no runtime variables are declared here.

Dependencies and integration points: Includes/dependencies: `asm/head.h`, `asm/kmap_size.h`. Integration points include memory-management; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are MMU/TLB encoding regressions, configuration-specific build gaps. Test signals: Boot memory layout, nocache allocator bounds, IO/DVMA mapping, PROM/debugger overlap checks, and fixed-address translation tests are signals.
