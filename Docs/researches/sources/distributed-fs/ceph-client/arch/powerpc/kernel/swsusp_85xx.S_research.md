# sources/distributed-fs/ceph-client/arch/powerpc/kernel/swsusp_85xx.S

## Purpose
Implements hibernation suspend/resume for Freescale BookE/e500-class 85xx systems.

## Important APIs, Types, and Functions
- `swsusp_save_area` stores SP, LR/CR, MSR, TCR, SPRG0-7, timebase, r2, and r12-r31.
- `swsusp_arch_suspend()` saves register/control state and calls `swsusp_save`.
- `swsusp_arch_resume()` copies pages, flushes data/instruction caches, invalidates TLBs, restores SPRGs/MSR/timebase/TCR, clears TSR pending bits, kicks decrementer, and returns.

## Control Flow and State
The resume path copies each `pbe` page using virtual addresses suitable for this BookE path, flushes caches via platform helpers, invalidates all TLBs because mappings may differ, restores special-purpose registers, restarts timer state, and restores saved nonvolatile registers.

## State and Persistence Behavior
Uses static `.data` save area and directly rewrites hardware SPRs and restored memory pages. It changes timer state by restoring TCR and clearing TSR bits.

## Dependencies and Integration Points
Depends on BookE SPR names, `_tlbil_all`, `flush_dcache_L1`, `flush_instruction_cache`, hibernation page backup structures, and generic `swsusp_save`.

## Risks
Incorrect TLB/cache flush ordering can execute stale instructions or use old translations. TCR/TSR restore must avoid pending timer/watchdog surprises after resume.

## Test Signals
Hibernate/resume on e500/e6500-class hardware, with timer interrupts enabled, large page-copy lists, and different MMU mappings after restore.
