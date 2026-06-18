<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/32/mmu-8xx.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/32/mmu-8xx.h

## Purpose
This header describes the Motorola/Freescale MPC8xx nohash MMU register interface and the Linux-side page-size/context contract for 8xx software-assisted TLB handling.

## Important APIs, Types, And Functions
It defines `SPRN_MI_*`, `SPRN_MD_*`, `SPRN_M_*`, `MI_*`, and `MD_*` masks for instruction/data TLB control, AP groups, EPN/TWC/RPN tablewalk state, CASID, and boot TLB setup. It exports `mm_context_t`, `struct mmu_psize_def`, `mmu_psize_defs[]`, `mmu_pin_tlb()`, `shift_to_mmu_psize()`, `mmu_psize_to_shift()`, vmap sizing hooks, and TLB-miss patch symbols.

## Control Flow
Runtime flow lives in assembly TLB miss handlers and MM setup code. This header supplies the register numbers and bit encodings used when handlers read miss state, compute page-table entries, write RPN registers to instantiate TLB entries, or patch optimized miss exits.

## State And Persistence Behavior
Persistent state includes per-mm context id/activity/vDSO/PTE fragment pointers and processor MMU SPR contents. Pinned TLB entries remain active until explicitly replaced or invalidated. `PHYS_IMMR_BASE` derives the internal memory map register base from `SPRN_IMMR`.

## Dependencies And Integration Points
It depends on page-size Kconfig, `linux/mmdebug.h`, `linux/sizes.h`, and common PowerPC MMU definitions. It integrates with 8xx TLB miss code, vmap/ioremap mapping size selection, KUAP/KUEP AP group policy, and boot-time TLB pinning.

## Risks And Edge Cases
AP group encodings are subtle and security-relevant. 16K page mode changes PTE fragmentation. Large vmap mappings require address, PFN, and maximum-shift alignment. Incorrect MI/MD bit definitions can produce silent memory permission, cacheability, or tablewalk corruption.

## Test Signals
Build and boot `CONFIG_PPC_8xx` with 4K and 16K pages, exercise vmalloc/ioremap mappings including 16K and 512K candidates, run user/kernel access permission tests, and stress TLB miss/refill and pinned kernel mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/32/mmu-8xx.h -->
