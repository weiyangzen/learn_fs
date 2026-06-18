# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/64/tlbflush-hash.h

Purpose: declares hash-MMU TLB and HPTE flush operations for Book3S64.

Important APIs/types/functions: provides hash flush declarations for TLB ranges, pages, mm contexts, hugepage invalidation, and low-level HPTE/hash range flushing used by page-table updates.

Control flow: implementation code performs HPTE invalidation and local/global flush decisions; this header exposes the interfaces to common pgtable and mm code.

State and persistence: affects hardware TLBs and hash page-table entries. No state is stored here.

Dependencies and integration points: depends on hash MMU structures, `mmu_gather`, VMA/MM types, and platform HPTE operations. It integrates with unmap, mprotect, page aging, and hugepage invalidation.

Risks: hash mode requires flushing both Linux-visible TLB effects and HPTE entries. Local/global flags must match CPU and hypervisor expectations to avoid stale translations on other CPUs.

Test signals: hash unmap/remap stress, SMP shootdown tests, THP/hugetlb invalidation, page aging tests, and pSeries/native HPTE backend validation.
