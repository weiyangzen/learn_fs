# sources/distributed-fs/ceph-client/arch/sparc/kernel/ktlb.S

Purpose: Contains SPARC64 kernel ITLB/DTLB miss fast paths for kernel mappings, including TSB lookups, vmalloc/module mapping walks, OBP translation handling, and sun4v patch points.

Important APIs/types/functions: Assembly entry labels include `kvmap_itlb`, `kvmap_itlb_4v`, `kvmap_dtlb`, `kvmap_dtlb_4v`, `kvmap_dtlb_nonlinear`, `kvmap_linear_early`, `kvmap_dtlb_tsb4m_load`, `kvmap_vmemmap`, and longpath labels for real faults. Macros such as `KERN_TSB_LOOKUP_TL1`, `KERN_TSB4M_LOOKUP_TL1`, `KERN_PGTABLE_WALK`, `OBP_TRANS_LOOKUP`, `TSB_LOCK_TAG`, and `TSB_WRITE` perform the MMU-specific work.

Control flow: ITLB misses read or receive the missing virtual address, reject NULL calls, probe the kernel TSB, fall back to page-table or OBP lookup, write a TSB entry, and load the TLB. DTLB misses first distinguish linear mapping addresses from nonlinear/vmalloc/module addresses, try the 4 MB TSB for linear mappings unless debug page allocation forces base pages, and otherwise page-table walk or signal a real fault. Long paths prepare processor state and branch to `sparc64_realfault_common` or `winfix_trampoline` for higher-level handling.

State and persistence: The code writes kernel TSB entries and IMMU/DMMU data-in ASIs, and uses `.sun4v_2insn_patch` sections so hypervisor systems replace direct ASI TLB loads with sun4v load paths. It reads global MMU constants such as `kern_linear_pte_xor`, `VMALLOC_END`, and optional `VMEMMAP_BASE`.

Dependencies and integration points: It depends on SPARC64 ASIs, TSB format, page tables, OBP translation tables, sun4v patching, sparsemem vmemmap, debug pagealloc, and low-level fault/trap assembly.

Risks and test signals: This is boot-critical code; a bad branch range, wrong context assumption, or wrong patched instruction corrupts kernel address translation. Tests are SPARC64 boot on sun4u and sun4v, vmalloc/module execution and data access, NULL kernel access faults, OBP mapping access, sparsemem vmemmap access, debug_pagealloc builds, and TLB miss stress under SMP.
