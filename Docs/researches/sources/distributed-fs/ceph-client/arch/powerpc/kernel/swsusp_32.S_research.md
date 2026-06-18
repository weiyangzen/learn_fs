# sources/distributed-fs/ceph-client/arch/powerpc/kernel/swsusp_32.S

## Purpose
Implements 32-bit classic PowerPC hibernation suspend/resume assembly for saving CPU registers, copying restored pages back, restoring timebase/MMU-related registers, flushing caches/TLBs, and returning to the restored kernel.

## Important APIs, Types, and Functions
- `swsusp_save_area` stores SP, LR/CR, MSR, SDR1, SPRGs, BATs, timebase, r2, and r12-r31.
- `swsusp_arch_suspend()` saves state and calls `swsusp_save`.
- `swsusp_arch_resume()` copies pages from `restore_pblist`, flushes/invalidate caches, restores saved control state, TLBs, timebase, decrementer, and callee-saved registers.
- `turn_on_mmu` uses SRR0/SRR1 and `rfi` to restore MSR/MMU state.

## Control Flow and State
Suspend saves register and MMU state, calls the generic hibernation save function, restores LR, and returns. Resume disables data translation to avoid hash/TLB misses while copying pages, iterates the page backup list, flushes L1 cache and TLBs, restores SPRG/SDR1/timebase, restarts decrementer, restores GPRs, and returns 0.

## State and Persistence Behavior
Uses a static save area in `.data` that survives until the restored image takes over. It directly writes BAT/SDR1/SPRG/timebase/decrementer state and physical memory pages.

## Dependencies and Integration Points
Depends on hibernation `restore_pblist`/`pbe_*` offsets, 32-bit MMU/BAT features, `swsusp_save`, `__nosave` layout, and cache/TLB assembly helpers.

## Risks
The file itself notes limitations around G5/750 MMU handling. Running with translation partially disabled and copying physical pages is highly sensitive to mappings, cache coherency, and identical loader/restored kernels.

## Test Signals
Hibernate/resume on classic 32-bit Book3S with and without high BATs, large memory, AltiVec users, and page lists spanning kernel/data text. Verify timebase and decrementer continue after resume.
