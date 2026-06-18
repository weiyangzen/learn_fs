<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/mmu-e500.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/mmu-e500.h

## Purpose
This header defines Freescale BookE/Book3E MMU constants, MAS/MMUCFG/TLBnCFG encodings, page-size support, and context data for nohash e500-style processors.

## Important APIs, Types, And Functions
It provides `BOOK3E_PAGESZ_*`, MAS0-MAS8 bit helpers, MMUCFG/MMUCSR0/TLBnCFG/TLBnPS masks, `TLBILX_T_*`, `MAS2_M_IF_NEEDED`, `tlbcam_index`, `mm_context_t`, `struct mmu_psize_def`, `shift_to_mmu_psize()`, `mmu_psize_to_shift()`, `mmu_virtual_psize`, `mmu_linear_psize`, `mmu_vmemmap_psize`, `struct tlb_core_data`, `linear_map_top`, `book3e_htw_mode`, `HUGETLB_NEED_PRELOAD`, and per-CPU `next_tlbcam_idx`.

## Control Flow
Low-level TLB management code uses these constants to program MAS registers, invalidate by TID/address/class, choose TLB entries, and decide page sizes. The inline page-size functions translate Linux shifts to MMU page-size indexes.

## State And Persistence Behavior
Persistent state includes per-mm ids, active flags, vDSO pointer, global and per-CPU TLB CAM indexes, software way-selection data, and 64-bit Book3E linear/vmemmap page-size choices.

## Dependencies And Integration Points
It depends on BookE CPU features, `asm/bug.h`, `asm/percpu.h`, and page-size Kconfig. It integrates with TLB miss handling, hugeTLB preload, SMP/coherent DMA policy, and 64-bit Book3E hardware tablewalk mode.

## Risks And Edge Cases
MAS bit definitions are hardware ABI. Coherency differs for SMP and e500mc DMA. Page-size support flags distinguish direct and indirect sizes. Per-core TLB locks must match e6500 handler expectations.

## Test Signals
Boot e500/e5500/e6500 variants, stress TLB invalidation and hugepage preloading, validate coherent DMA, inspect MAS programming through debug traces, and run SMP page-fault stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/mmu-e500.h -->
