# sources/distributed-fs/ceph-client/arch/arm64/include/asm/tlbflush.h
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/tlbflush.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/tlbflush.h` Implements arm64 TLB invalidation primitives, TLBI instruction wrappers, range invalidation, TTL hints, KPTI user-ASID invalidation, batched unmap synchronization, and erratum-specific SME DVMSync handling. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
__tlbi(), __tlbi_user(), __TLBI_VADDR(), get_trans_granule(), sme_dvmsync*(), TLBI_TTL_* and tlbi_op, vae*/vale*/ipas* helpers, __tlbi_level_asid(), TLBIR_* range fields, __flush_tlb_range_op(), TLBF_* flags, local_flush_tlb_all(), flush_tlb_all(), flush_tlb_mm(), arch_tlbbatch_should_defer(), arch_tlbbatch_flush(), __flush_tlb_range(), flush_tlb_range(), __flush_tlb_page(), flush_tlb_kernel_range(), __flush_tlb_kernel_pgtable(), arch_tlbbatch_add_pending(), pte_needs_flush(), huge_pmd_needs_flush(). The file is 758 lines / 21398 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
Flushes follow DSB-before, TLBI, DSB-after, and optional ISB. Range flushing uses FEAT_TLBIRANGE when available, handles LPA2 64K alignment, falls back to per-entry operations, and escalates excessive ranges to full ASID/global flushes. Flags select walk-cache invalidation, notifier calls, sync elision, and local-only invalidation.

### State, Persistence, And Dependencies
No owned storage except optional batch cpumask managed elsewhere. Side effects are architectural TLB and walk-cache invalidations, mmu notifier secondary invalidations, and erratum DVMSync IPIs. Depends on bitfield, mm_types, sched, mmu_notifier, cputype, mmu, stage2/KVM LPA2 helpers, cpufeature alternatives; integrates with pgtable.h, tlb.h, KVM stage-2, mmu_gather, KPTI, MTE/SME errata, and secondary TLB notifiers.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
Ordering bugs cause stale translations; wrong TTL/range/LPA2 encoding can miss invalidations; TLBF_NOSYNC must only be used when later synchronization is guaranteed; notifier suppression can break IOMMU/KVM secondary TLBs.

### Test Signals
Run TLB shootdown stress, munmap/mprotect/THP collapse, KVM/IOMMU notifier tests, LPA2 and TLBIRANGE hardware/emulation, KPTI configs, erratum configs, and pte_needs_flush permission-transition tests.
