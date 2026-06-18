## sources/distributed-fs/ceph-client/arch/s390/mm/pgtable.c

Purpose: implements s390 page-table entry exchange, TLB invalidation, DAT protection reset, hugepage table exchange helpers, write-combine protection, and THP deposited page-table handling.

Important APIs, types, and functions: exported APIs include `pgprot_writecombine()`, `ptep_xchg_direct()`, `ptep_reset_dat_prot()`, `ptep_xchg_lazy()`, `ptep_modify_prot_start()`, `ptep_modify_prot_commit()`, `pmdp_xchg_direct()`, `pmdp_xchg_lazy()`, `pudp_xchg_direct()`, and THP `pgtable_trans_huge_deposit()`/`pgtable_trans_huge_withdraw()`. Internal invalidation helpers include local/global IPTE and IDTE variants.

Control flow: PTE flush helpers read the old entry, skip invalid entries, increment `mm->context.flush_count`, choose local invalidation when the mm is only on the current CPU and the CPU supports local TLB control, otherwise issue global invalidation. Lazy paths can mark entries invalid and set `flush_mm` when only attached locally, deferring full work. Exchange APIs disable preemption, flush, set the new entry, and re-enable preemption. RDP reset clears hardware protect without invalidating the entry, then writes only software-bit changes.

State and persistence: mutates PTE/PMD/PUD entries, `mm->context.flush_count`, `mm->context.flush_mm`, and THP `pmd_huge_pte()` FIFO list state. `pgprot_writecombine()` uses the global `mio_wb_bit_mask`.

Dependencies and integration points: depends on s390 IPTE/IDTE/RDP instructions, machine guest-TLB support, gmap ASCE state, mm CPU masks, TLB local-control facility, THP, KSM/sysctl includes, and MIO write-combine bit from PCI/MMIO support.

Risks: invalidation options must match host vs guest ASCE state; wrong NODAT/GUEST_ASCE selection can leave stale guest translations. Lazy invalidation relies on CPU attach masks. RDP may only be used when the new PTE differs in permitted bits. THP deposit/withdraw assumes PMD lock and FIFO list layout embedded in page-table memory.

Test signals: mprotect/protection change stress, KVM guest TLB invalidation, THP split/collapse, local-vs-global flush paths on SMP, write-combine mappings for MIO devices, and RDP-specific protect-bit reset behavior.
