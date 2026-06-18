# sources/distributed-fs/ceph-client/arch/arm/mm/proc-arm922.S

## Purpose
This file provides ARM922T processor hooks, mirroring the ARM920T MMU/cache model with ARM922-specific cache geometry and CPU ID.

## Important APIs, Types, and Functions
It defines `cpu_arm922_*`, `arm922_*` cache/coherency/DMA functions, `arm922_crval`, and `arm922_processor_functions`. The proc-info entry matches `0x41009220`, uses `v4t_early_abort` and `legacy_pabort`, and publishes ARMv4T hwcaps.

## Control Flow
Setup invalidates caches/TLBs and returns the desired SCTLR value. Runtime cache and DMA calls operate through the installed cache function table; `switch_mm()` cleans/invalidates cache state, writes the new page-table base, and flushes TLBs.

## State and Persistence Behavior
Hardware state changed includes cache contents, write buffer, TLB, CP15 c1/c2, and hardware PTE cache lines. Static proc/function tables remain in kernel memory.

## Dependencies and Integration Points
The file integrates with ARM CPU probing, generic cacheflush and DMA APIs, v4 TLB/user helper tables, and `proc-macros.S`.

## Risks
The comments and constants must align with actual cache segment counts. A wrong D-cache limit or line size can skip required maintenance. Context switching depends on complete cache/TLB invalidation for correctness.

## Test Signals
Boot ARM922T builds, run process/context switch stress, DMA mapping tests, executable mapping changes, and cache flush API tests. Confirm proc-info identifies the CPU and uses the expected cache function table.
