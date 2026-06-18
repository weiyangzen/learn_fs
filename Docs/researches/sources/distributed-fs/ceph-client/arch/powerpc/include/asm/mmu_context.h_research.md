# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/mmu_context.h

Purpose: declares and implements PowerPC mm context lifecycle, context switching, SPAPR TCE IOMMU preregistration, radix/hash switch hooks, copro/VA window accounting, KVM radix invalidation hooks, and pkey duplication/access checks.

Important APIs/types/functions: `init_new_context`, `destroy_context`, SPAPR IOMMU helpers (`mm_iommu_new`, `mm_iommu_lookup`, `mm_iommu_ua_to_hpa`, etc.), `switch_slb`, `radix__switch_mmu_context`, `switch_mmu_context`, hash context allocation/reservation/destruction, `alloc_extended_context`, `need_extra_context`, active CPU and copro counters, VAS window add/remove helpers, `do_h_rpt_invalidate_prt`, `switch_mm`, `activate_mm`, `enter_lazy_tlb` for Book3E 64, `arch_exit_mmap`, pkey hooks, and `arch_dup_mmap`.

Control flow: process creation initializes mm context; scheduler context switches disable interrupts and call `switch_mm_irqs_off`, which selects radix context switching or SLB switching. Coprocessor/VAS users increment counters to force global invalidations and decrement them after flushing on radix.

State and persistence: state lives in `mm->context`: context IDs, extended IDs, active CPU counts, copro and VAS window counters, pkey state, and optional IOMMU preregistration memory. PACA may hold current PGD in Book3E lazy TLB mode.

Dependencies and integration points: depends on scheduler, mm, spinlock, CPU features, MMU headers, SPAPR TCE IOMMU, radix/hash TLB flush, VAS/nest MMU, KVM radix invalidation, and generic mmu context code.

Risks: context switching must run with correct interrupt state. Imbalanced copro/VAS add/remove can force global flushes forever or under-flush nest MMU translations. Extended context allocation is hash-64 specific. Stub behavior must be correct on non-Book3S configurations.

Test signals: fork/exec/mmap stress, context switch with hash and radix, SPAPR VFIO/IOMMU preregistration tests, VAS/copro TLB invalidation tests, pkeys selftests, and KVM H_RPT_INVALIDATE coverage.
