# sources/distributed-fs/ceph-client/arch/sparc/include/asm/tsb.h

Purpose: sparc64 Translation Storage Buffer assembly macro header defining TSB entry format, lock/invalid tag bits, physical-load patch tables, kernel/user page-table walks, huge-page propagation, OBP lookup, and kernel TSB lookup.

Important APIs/types/functions: types `tsb_ldquad_phys_patch_entry`, `tsb_phys_patch_entry`; macros/constants `_SPARC64_TSB_H`, `TSB_TAG_LOCK_BIT`, `TSB_TAG_LOCK_HIGH`, `TSB_TAG_INVALID_BIT`, `TSB_TAG_INVALID_HIGH`, `TSB_LOAD_QUAD`, `TSB_LOAD_TAG_HIGH`, `TSB_LOAD_TAG`, `TSB_CAS_TAG_HIGH`, `TSB_CAS_TAG`, `TSB_STORE`, `TSB_LOCK_TAG`, `TSB_WRITE`, `KERN_PGTABLE_WALK`, `USER_PGTABLE_CHECK_PUD_HUGE`, `USER_PGTABLE_CHECK_PMD_HUGE`, `USER_PGTABLE_WALK_TL1`, `OBP_TRANS_LOOKUP`, plus 5 more.

Control flow: The file is driven by preprocessor gates such as `_SPARC64_TSB_H`, `__ASSEMBLER__`, `defined(CONFIG_HUGETLB_PAGE) || defined(CONFIG_TRANSPARENT_HUGEPAGE)`, `CONFIG_DEBUG_PAGEALLOC`; inline/assembler paths that run at trap, MMU, cache, lock, or user-copy boundaries. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into memory-management, TLB/MMU paths rather than through standalone functions.

State and persistence behavior: State is TSB tag/PTE slots protected by tag lock bits, patch-section records for physical load variants, swapper TSBs, and PROM translation tables.

Dependencies and integration points: Includes/dependencies: none beyond compiler-visible SPARC/kernel types. Integration points include memory-management, TLB/MMU; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are inline assembly or ASI ordering mistakes, MMU/TLB encoding regressions, configuration-specific build gaps. Test signals: TLB miss handler tests, TSB conflict/lock stress, huge-page misses, OBP mappings, sun4u/sun4v physical load patching, and DEBUG_PAGEALLOC variants are signals.
