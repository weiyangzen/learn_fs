# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/64/hugetlb.h

Purpose: provides Book3S64 hugetlb helpers for translating Linux hugepage sizes to MMU page-size indexes and dispatching radix-specific hugepage TLB/protection operations.

Important APIs/types/functions: declares `radix__flush_hugetlb_page()`, `radix__local_flush_hugetlb_page()`, `radix__huge_ptep_modify_prot_commit()`, `huge_ptep_modify_prot_start()`, and `huge_ptep_modify_prot_commit()`. Inline helpers include `hstate_get_psize()`, `gigantic_page_runtime_supported()`, `flush_hugetlb_page()`, `check_and_get_huge_psize()`, and `arch_has_huge_bootmem_alloc()`.

Control flow: `hstate_get_psize()` maps a hugepage shift to `MMU_PAGE_2M`, `1G`, `16M`, or `16G`, warning and falling back to `mmu_virtual_psize` on mismatch. `check_and_get_huge_psize()` rejects firmware page sizes unsupported by the active MMU: radix allows 2M/1G, hash allows 16M/16G. Runtime gigantic allocation is disabled for hash LPARs.

State and persistence: no private state is stored. The helpers act on hugetlb VMA/PTE state and firmware/MMU page-size definitions.

Dependencies and integration points: depends on firmware feature checks, `radix_enabled()`, `mmu_psize_defs`, hugetlb hstate data, and Book3S64 page-table code. It integrates hugetlbfs, boot-time hugepage reservation, and radix TLB flush/protection paths.

Risks: accepting an unsupported hugepage shift would create page-table entries the active MMU cannot represent. Hash LPAR gigantic pages require hypervisor-assisted reservation and are not safe for runtime allocation.

Test signals: hugetlbfs tests for radix 2M/1G and hash 16M/16G, boot-time hugepage reservation on LPAR hash systems, runtime allocation rejection tests, and hugepage permission-change flush tests.
