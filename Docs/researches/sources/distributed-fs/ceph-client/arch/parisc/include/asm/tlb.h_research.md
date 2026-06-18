<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/tlb.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/tlb.h

Source read size: 12 lines, 327 bytes.

Purpose: wires PA-RISC page-table freeing into the generic MMU-gather TLB interface. Important APIs: includes `asm-generic/tlb.h`, defines `__pmd_free_tlb()` for three-level page tables, and defines `__pte_free_tlb()`. Control flow: generic MM teardown queues freed page-table descriptors through `tlb_remove_ptdesc()` rather than immediately freeing raw pages. State and persistence: the file does not hold state; it controls deferred freeing lifetime during MMU gather batches. Dependencies and integration points: relies on `virt_to_ptdesc()`, `page_ptdesc()`, and `CONFIG_PGTABLE_LEVELS`. Risks: incorrect ptdesc conversion can corrupt page-table memory reclamation or cause use-after-free with concurrent TLB walkers. Test signals: mm teardown stress, fork/exec/exit loops, high VMA churn, three-level page table builds, and KASAN/KFENCE page-table lifetime checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/tlb.h -->
