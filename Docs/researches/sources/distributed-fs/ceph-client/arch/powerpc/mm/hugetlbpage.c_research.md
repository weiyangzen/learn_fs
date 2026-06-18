# sources/distributed-fs/ceph-client/arch/powerpc/mm/hugetlbpage.c

Purpose: provides common PowerPC HugeTLB support, including huge PTE allocation, valid hugepage-size discovery, pseries boot-time gigantic page handling, and CMA sizing.

Important APIs and control flow: `huge_pte_offset()` finds existing huge PTEs via the Linux page-table walker. `huge_pte_alloc()` allocates folded or real PUD/PMD/PTE levels according to hugepage size and has an 8xx contiguous-PTE path. `pseries_add_gpage()` records firmware-provided gigantic pages until `pseries_alloc_bootmem_huge_page()` can add them to `huge_boot_pages`. `hugetlbpage_init()` registers all hardware-supported huge sizes unless disabled or unsupported by hash MMU.

State and dependencies: state includes `hugetlb_disabled`, early `gpage_freearray`, `nr_gpages`, huge hstates, and MMU page-size definitions. It depends on firmware LPAR detection, radix/hash mode, memblock, hugetlb core, and pte allocation helpers. Risks are registering unsupported sizes, exhausting the fixed gigantic-page array, 8xx contiguous mapping mistakes, and wrong CMA order for radix versus 16G hash pages. Test signals include hugetlb boot parameters, pseries expected-pages, 8xx hugepages, multiple hstates, and CMA reservation checks.
