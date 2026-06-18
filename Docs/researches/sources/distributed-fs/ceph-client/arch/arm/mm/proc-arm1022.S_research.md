# sources/distributed-fs/ceph-client/arch/arm/mm/proc-arm1022.S

## Purpose
This file supplies ARM1022E low-level MMU/cache/TLB operations, closely following the ARM1020E pattern with a distinct CPU ID and name.

## Important APIs, Types, and Functions
The public hooks are `cpu_arm1022_proc_init`, `cpu_arm1022_proc_fin`, `cpu_arm1022_reset`, `cpu_arm1022_do_idle`, `cpu_arm1022_dcache_clean_area`, `cpu_arm1022_switch_mm`, `cpu_arm1022_set_pte_ext`, and the `arm1022_*` cache/DMA/coherency helpers. `arm1022_crval` drives setup. `__arm1022_proc_info` matches `0x4105a220` and advertises ARMv5TE EDSP-capable features.

## Control Flow
After proc-info match, setup invalidates cache/TLB state and derives the SCTLR value. The runtime function table routes generic cacheflush, TLB, page-table, and reset requests to the ARM1022 implementations.

## State and Persistence Behavior
The file changes hardware CPU state: SCTLR, TTB, TLB entries, cache contents, and hardware PTE words. Its tables are static kernel metadata.

## Dependencies and Integration Points
It depends on `proc-macros.S`, v4/v5 CP15 maintenance operations, `legacy_pabort`, `v4t_early_abort`, and v4 write-back helper tables. It integrates with generic ARM MM through `processor_functions`.

## Risks
Its whole-cache and range-cache paths assume the same geometry constants as ARM1020E. Incorrect PTE cleanup or write-buffer drain can expose stale hardware entries. The CPUID mask must not overlap unrelated ARM10 variants.

## Test Signals
Boot on ARM1022E-capable hardware, verify CPU identification and hwcap output, run page-fault, context-switch, cache-coherency, DMA, and reset/kexec tests. Build with cache-disable and write-through options to cover conditional paths.
