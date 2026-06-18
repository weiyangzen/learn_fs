<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/tlbbatch.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/tlbbatch.h

Purpose: defines x86 architecture state for deferred TLB unmap batching. Important type is `arch_tlbflush_unmap_batch`, containing a CPU mask and `unmapped_pages` flag.

Control flow: unmap paths accumulate CPUs that may hold stale translations and later flush them as a batch. State is temporary batch metadata. Dependencies include cpumasks, generic MMU gather, and x86 TLB flush code.

Risks include losing CPUs from the mask, failing to flush unmapped pages, or over-flushing under heavy munmap. Test signals include TLB gather stress, remote CPU unmap batching, mmu_gather tests, and memory reclaim under SMP.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/tlbbatch.h -->
