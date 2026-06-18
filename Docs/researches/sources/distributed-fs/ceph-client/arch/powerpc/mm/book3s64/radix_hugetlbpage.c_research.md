# sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s64/radix_hugetlbpage.c

Purpose: Provides radix-specific hugetlb TLB flushing and protection-commit behavior.

Important APIs and functions: `radix__flush_hugetlb_page()`, `radix__local_flush_hugetlb_page()`, `radix__flush_hugetlb_tlb_range()`, and `radix__huge_ptep_modify_prot_commit()` are the file's public operations. They derive page size from the hugetlb hstate and delegate to radix TLB helpers.

Control flow: Single-page flush reads the VMA file hstate, gets the PowerPC page-size index, and calls global or local radix page-size flush. Range flush uses PWC flush when the range is at least `PUD_SIZE`, otherwise normal page-size range flush, then invalidates secondary MMU notifier TLBs. Protection commit checks for POWER9 NMMU relaxed-permission erratum: if the new PTE is a RW upgrade and the mm has coprocessor users, it flushes before setting the new huge PTE. It then calls `set_huge_pte_at()`.

State and persistence: No private persistent state. It observes `mm->context.copros` and hugetlb hstate metadata and mutates hugetlb PTEs through generic setters.

Dependencies and integration: Called by common hugetlb code in `hugetlbpage.c` and generic hugetlb/radix flush paths. Integrates with `mmu_notifier_arch_invalidate_secondary_tlbs()` for secondary TLB consumers.

Risks: Page-size selection must match the hstate or the wrong radix flush encoding may be used. POWER9 NMMU requires a flush before permission relaxation for coprocessor contexts; missing that can leave secondary translations with stale permissions.

Test signals: hugetlb mprotect RW upgrades with active coprocessor/NMMU users, local and global flush tests, PUD-sized range invalidations, and secondary MMU notifier validation.
