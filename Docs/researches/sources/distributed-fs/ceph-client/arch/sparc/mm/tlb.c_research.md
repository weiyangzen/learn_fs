# sources/distributed-fs/ceph-client/arch/sparc/mm/tlb.c

Purpose: implements SPARC64 software batching for TLB and TSB invalidations, plus transparent-hugepage PMD accounting and split/deposit helpers.

Important APIs/functions: key functions are `flush_tlb_pending()`, `arch_enter_lazy_mmu_mode()`, `arch_flush_lazy_mmu_mode()`, `arch_leave_lazy_mmu_mode()`, `tlb_batch_add()`, internal `tlb_batch_add_one()`, and THP helpers `set_pmd_at()`, `pmdp_invalidate()`, `pgtable_trans_huge_deposit()`, and `pgtable_trans_huge_withdraw()`. Per-CPU state is `struct tlb_batch tlb_batch`.

Control flow: lazy MMU mode disables preemption and accumulates virtual addresses for one `mm`. When the batch fills, changes `mm`, changes hugepage shift, or leaves lazy mode, `flush_tlb_pending()` flushes matching TSB entries first and then performs local or SMP TLB shootdown. `tlb_batch_add()` also handles D-cache alias flushes for dirty file-backed pages before queuing the TLB invalidation.

State and persistence: state is per-CPU batching metadata: target `mm`, address count, hugepage shift, and address array. THP counters live in `mm->context.thp_pte_count` and `hugetlb_pte_count`.

Dependencies and integration points: depends on generic MMU-gather/lazy-MMU hooks, SPARC64 TSB code, `global_flush_tlb_page()`, `smp_flush_tlb_pending()`, `__flush_tlb_pending()`, cache alias helpers, and THP page-table APIs.

Risks: batching must not mix address spaces or hugepage granularities. Missing TSB invalidation can repopulate stale TLB entries. D-cache alias handling depends on physical/virtual color checks. THP counter imbalance can prevent correct huge TSB allocation.

Test signals: run KUnit lazy-MMU tests, THP split/collapse stress, hugetlb and huge-zero-page faults, SMP mmap/munmap/mprotect workloads, file-backed dirty-page alias tests, and non-SMP builds.
