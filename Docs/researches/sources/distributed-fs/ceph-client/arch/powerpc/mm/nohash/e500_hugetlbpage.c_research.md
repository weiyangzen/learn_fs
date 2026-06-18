# sources/distributed-fs/ceph-client/arch/powerpc/mm/nohash/e500_hugetlbpage.c

Purpose: preloads e500 Book3E HugeTLB entries into TLB1/CAM hardware after hugetlb page faults.

Important APIs and control flow: `__update_mmu_cache()` calls `book3e_hugetlb_preload()` when the VMA is hugetlb. The preload path disables IRQs, optionally takes an SMT-safe PACA lock, checks whether a matching TLB entry already exists, picks the next TLB1 slot, programs MAS0-MAS3/MAS7 from the VMA page size and PTE attributes, writes `tlbwe`, and unlocks. `flush_hugetlb_page()` invalidates one hugepage-sized TLB entry.

State and dependencies: state includes per-PACA or per-CPU next CAM indices, SMT lock bytes, TLB core data, and PTE dirty/access bits. It depends on MAS SPR access, `vma_mmu_pagesize()`, hugepage hstates, MMU context IDs, and nohash flush helpers. Risks are racing SMT siblings without locks, evicting critical CAM entries, preserving write permissions for clean PTEs, and missing invalidations on size mismatches. Test signals include e500 hugetlb mmap/fault/unmap, SMP/SMT hugepage stress, dirty-bit transitions, and TLB miss rates.
