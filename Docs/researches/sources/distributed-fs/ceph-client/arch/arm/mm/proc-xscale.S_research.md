# sources/distributed-fs/ceph-client/arch/arm/mm/proc-xscale.S

## Purpose
Implements the original Intel XScale processor backend, covering cache maintenance, DMA cache synchronization, page-table switching, PTE attribute construction, suspend/resume, setup, and CPU identification records for 80200, IOP, IXP, and PXA families.

## Important APIs, Types, And Functions
Exports `cpu_xscale_proc_init`, `cpu_xscale_proc_fin`, `cpu_xscale_reset`, `cpu_xscale_do_idle`, `xscale_flush_*`, `xscale_coherent_*`, `xscale_dma_map_area`, `xscale_80200_A0_A1_dma_map_area`, `xscale_dma_unmap_area`, `cpu_xscale_dcache_clean_area`, `cpu_xscale_switch_mm`, `cpu_xscale_set_pte_ext`, suspend/resume hooks, and `__xscale_setup`.

## Control Flow
Initialization re-enables write buffer coalescing and setup invalidates caches/TLBs, grants CP6/CP13 access, and computes SCTLR bits from `xscale_crval`. Whole-cache cleaning uses the alternating `clean_addr` line-allocation workaround. Range operations loop over 32-byte lines and drain write buffers. DMA map chooses clean, invalidate, or flush based on DMA direction, with an 80200 A0/A1 erratum path that flushes instead of invalidating. PTE writes translate Linux memory types through `cpu_xscale_mt_table` and apply erratum 40 by forcing user read-only writeback pages to writethrough.

## State, Dependencies, And Integration
State includes CP15 cache/TLB/SCTLR/ACTLR/domain/TTBR/PID registers, CP14 clock/idle state, and the `clean_addr` data word used to alternate cleaning ranges. Integrates with `v4wbi_tlb_fns`, `xscale_mc_user_fns`, `xscale_cache_fns`, and the CPU proc-info matching table.

## Risks And Test Signals
Risks include subtle dirty-line loss, erratum handling regressions, incorrect endian or PTE memory type encoding, and reset code alignment hazards after MMU disable. Test signals include boot across XScale variants, DMA tests on unaligned buffers, executable mapping coherency, user read-only mapping behavior, suspend/resume, and large cache flush paths.
