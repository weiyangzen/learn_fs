# sources/distributed-fs/ceph-client/arch/arm/mm/proc-arm926.S

## Purpose
This file implements ARM926EJ-S MMU/cache/TLB, DMA, idle, and suspend/resume hooks.

## Important APIs, Types, and Functions
It defines `cpu_arm926_*`, `arm926_*` cache/coherency/DMA helpers, `cpu_arm926_do_suspend()`, `cpu_arm926_do_resume()`, `arm926_crval`, and `arm926_processor_functions`. The proc-info entry matches `0x41069260`, uses `v5tj_early_abort` and `legacy_pabort`, and advertises FAST_MULT, EDSP, and JAVA.

## Control Flow
Setup invalidates caches/TLBs, optionally disables write-back, and computes SCTLR bits. Idle drains the write buffer, disables I-cache with FIQs masked, waits for interrupt, then restores I-cache and FIQ state. `switch_mm()` performs full D/I cache maintenance, writes the page-table base, and invalidates TLBs. Suspend/resume saves and restores PID/domain/control state.

## State and Persistence Behavior
The file persists CPU metadata and mutates CP15 state, caches, TLBs, translation base, and hardware PTE cache lines. Suspend state is stored in caller-provided memory.

## Dependencies and Integration Points
It integrates with generic ARM MM, v4 write-back helper tables, suspend code, abort handlers, DMA/cache APIs, and `proc-macros.S`.

## Risks
Idle temporarily disables I-cache and masks FIQs; ordering is important. Cache maintenance differs for write-through and write-back builds. Incorrect JAVA/EDSP hwcaps or abort handler selection can mislead userland or fault handling.

## Test Signals
Boot ARM926EJ-S systems, run suspend/resume, WFI idle, DMA, mmap, fork/exec, and JIT/executable-page tests. Verify CPU capability output and no stale instruction fetches.
