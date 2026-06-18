# sources/distributed-fs/ceph-client/arch/arm/mm/proc-feroceon.S

## Purpose
This file provides Marvell Feroceon low-level MMU/cache/TLB/DMA support, including optional Feroceon L2 cache maintenance and multiple CPU ID variants.

## Important APIs, Types, and Functions
It defines `cpu_feroceon_*` hooks, `feroceon_*` cache/coherency/DMA helpers, range-specific L2 helpers, suspend/resume hooks, `feroceon_crval`, and `feroceon_processor_functions`. The proc-info macro emits entries for old Feroceon IDs and 88FR531/88FR571/88FR131 variants, with ARMv5TE hwcaps.

## Control Flow
Setup invalidates caches/TLBs and computes SCTLR bits. Runtime cache/DMA operations maintain L1 and, when configured, Feroceon L2 lines. `switch_mm()` cleans relevant caches, writes TTB, and invalidates TLBs. Suspend/resume saves and restores CP15 state.

## State and Persistence Behavior
The file mutates L1/L2 cache state, CP15 control/TTB/TLB/PTE state, and stores suspend snapshots in caller memory. Processor metadata remains static.

## Dependencies and Integration Points
It depends on Marvell Feroceon cache extensions, optional `CONFIG_CACHE_FEROCEON_L2`, ARMv5TE helper tables, generic DMA/cache APIs, and legacy abort handling.

## Risks
L2 write-through/write-back configuration changes which operations are needed. Missing range L2 maintenance can corrupt DMA. Multiple CPUID entries increase match-order risk. Suspend/resume and switch-mm paths must keep L1, L2, TLB, and TTB ordering correct.

## Test Signals
Boot Feroceon variants with L2 enabled/disabled and write-through/write-back settings. Run network/storage DMA stress, page-table churn, suspend/resume, and executable coherency tests. Inspect CPU name and cache function selection.
