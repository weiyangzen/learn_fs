# sources/distributed-fs/ceph-client/arch/sparc/include/asm/spitfire.h

Purpose: sparc64 UltraSPARC/Spitfire/Cheetah/SUN4V MMU/cache register header with TLB tag/data accessors, cache flush helpers, chip IDs, LSU control bits, and D-cache alias flags.

Important APIs/types/functions: functions/helpers `cheetah_enable_pcache`, `spitfire_put_dcache_tag`, `spitfire_put_icache_tag`, `spitfire_get_dtlb_data`, `spitfire_get_dtlb_tag`, `spitfire_put_dtlb_data`, `spitfire_get_itlb_data`, `spitfire_get_itlb_tag`, `spitfire_put_itlb_data`, `spitfire_flush_dtlb_nucleus_page`, `spitfire_flush_itlb_nucleus_page`, `cheetah_flush_dtlb_all`, `cheetah_flush_itlb_all`, `cheetah_get_ldtlb_data`, `cheetah_get_litlb_data`, `cheetah_get_ldtlb_tag`, plus 9 more; macros/constants `_SPARC64_SPITFIRE_H`, `TSB_TAG_TARGET`, `TLB_SFSR`, `TSB_REG`, `TLB_TAG_ACCESS`, `VIRT_WATCHPOINT`, `PHYS_WATCHPOINT`, `TSB_EXTENSION_P`, `TSB_EXTENSION_S`, `TSB_EXTENSION_N`, `TLB_TAG_ACCESS_EXT`, `PRIMARY_CONTEXT`, `SECONDARY_CONTEXT`, `DMMU_SFAR`, `SPITFIRE_HIGHEST_LOCKED_TLBENT`, `CHEETAH_HIGHEST_LOCKED_TLBENT`, `L1DCACHE_SIZE`, `SUN4V_CHIP_INVALID`, plus 21 more.

Control flow: The file is driven by preprocessor gates such as `_SPARC64_SPITFIRE_H`, `CONFIG_SPARC64`, `__ASSEMBLER__`; inline/assembler paths that run at trap, MMU, cache, lock, or user-copy boundaries; static inline helpers selected by generic kernel call sites. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into memory-management, TLB/MMU paths rather than through standalone functions.

State and persistence behavior: State is architectural MMU/cache registers, TLB entries, CPU implementation ids, and global flags such as `tlb_type`/cache aliasing.

Dependencies and integration points: Includes/dependencies: `asm/asi.h`. Integration points include memory-management, TLB/MMU; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are inline assembly or ASI ordering mistakes, MMU/TLB encoding regressions, configuration-specific build gaps. Test signals: Boot patching across sun4u/sun4v, TLB dump/flush, cache enable/disable, LSU control, and Niagara chip detection are tests.
