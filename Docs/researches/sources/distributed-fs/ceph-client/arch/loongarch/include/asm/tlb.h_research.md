<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/tlb.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/tlb.h

Purpose: defines LoongArch TLB batching, refill, and MMU gather integration.
Important APIs and types: declares TLB handler symbols, `tlb_init`, `setup_tlb_handler`, `local_flush_tlb_*`, huge TLB helpers, and generic `tlb_gather_mmu` integration macros.
Control flow: memory unmap paths batch page-table freeing and TLB invalidations; architecture flush functions invalidate local or remote TLB entries according to range/mm scope.
State and persistence: TLB state lives in hardware and per-mm ASID/context data; this header defines how generic MM requests invalidation.
Dependencies and integration: integrates with `tlbflush.h`, page-table definitions, ASID allocation, exception refill assembly, huge pages, and SMP shootdown.
Risks and test signals: stale TLBs cause memory corruption/security bugs; over-flushing hurts performance. Signals include mmap/munmap stress, fork/exit, THP, KVM, ASID wrap, and SMP shootdown tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/tlb.h -->
