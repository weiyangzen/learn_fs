# sources/distributed-fs/ceph-client/arch/arc/include/asm/tlb.h

ARC TLB gather glue. It includes linux/pagemap.h and asm-generic/tlb.h without adding custom state. Control flow is generic mmu_gather and page-table teardown using generic implementation, while actual flush primitives are declared in tlbflush.h. Dependencies are generic TLB batching and ARC flush implementations. Risks are hidden if ARC needs stronger ordering than generic tlb gather supplies. Test signals are munmap/mprotect/unmap stress, page-table freeing under memory pressure, and SMP TLB shootdown coverage.
