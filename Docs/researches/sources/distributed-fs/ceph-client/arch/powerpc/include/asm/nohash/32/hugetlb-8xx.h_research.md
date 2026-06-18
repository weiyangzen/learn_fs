# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/32/hugetlb-8xx.h

Purpose: implements 32-bit 8xx nohash hugepage architecture hooks.

Important APIs/types/functions: `PAGE_SHIFT_8M` defines 8 MiB hugepage shift. Helpers include `flush_hugetlb_page`, `check_and_get_huge_psize`, `set_huge_pte_at`, `huge_ptep_get`, `huge_pte_clear`, `huge_ptep_set_wrprotect`, and 4K-page-only `arch_make_huge_pte`.

Control flow: hugetlb code flushes TLBs through normal page flush, maps shifts to MMU page sizes, sets/gets/clears huge PTEs, write-protects entries through `pte_update`, and for 4K base pages marks 16K or larger huge PTEs with `_PAGE_SPS`/`_PAGE_HUGE`.

State and persistence: mutates page-table entries for huge mappings; no independent state.

Dependencies and integration points: depends on 8xx page-table helpers such as `ptep_is_8m_pmdp`, `pte_offset_kernel`, `ptep_get`, `pte_update`, and hugepage MMU page-size conversion.

Risks: 8 MiB huge PTEs may be represented at PMD-like locations, so `huge_ptep_get()` must adjust for aligned addresses. Wrong `_PAGE_SPS`/`_PAGE_HUGE` selection breaks 8xx TLB loading.

Test signals: hugetlbfs tests on PPC 8xx, 16K and 8M hugepage mappings, write-protect/COW behavior, TLB flush correctness, and 4K base-page build coverage.
