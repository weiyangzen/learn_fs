<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/tlb.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/tlb.h

Purpose: provides x86 MMU gather flush glue and INVLPG/INVLPGB helpers. Important APIs include `tlb_flush()`, `invlpg()`, `__invlpgb()`, `__tlbsync()`, `invlpgb_flush_user_nr_nosync()`, `invlpgb_flush_single_pcid_nosync()`, `invlpgb_flush_all()`, `invlpgb_flush_addr_nosync()`, and `invlpgb_flush_all_nonglobals()`.

Control flow: generic unmap batching calls `tlb_flush()` to choose full-mm or range flushing through `flush_tlb_mm_range()`. Broadcast TLB flush configurations use INVLPGB to invalidate by VA/PCID/ASID and TLBSYNC to wait for completion, with preemption guarded where required.

State and persistence: mutates CPU/system TLB state only. Dependencies include generic `mmu_gather`, page/vDSO bits, broadcast TLB flush feature, x86 INVLPGB/TLBSYNC instruction encoding, and migration/preemption constraints.

Risks: missing synchronization leaves stale translations; incorrect ASID/PCID/VA flags invalidate too much or too little; migration during TLBSYNC can miss pending invalidations. Test signals include mmap/munmap stress, broadcast TLB flush capable CPUs, PCID tests, hugepage unmap, memory hotplug, and TLB shootdown selftests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/tlb.h -->
