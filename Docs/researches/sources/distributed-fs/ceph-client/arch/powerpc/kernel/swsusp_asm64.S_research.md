# sources/distributed-fs/ceph-client/arch/powerpc/kernel/swsusp_asm64.S

## Purpose
Implements 64-bit PowerPC hibernation suspend/resume assembly for Book3S and non-Book3S 64-bit variants.

## Important APIs, Types, and Functions
- `swsusp_save_area` stores r1/r2/r12-r31/r13, LR/CR/XER/MSR, timebase, SDR1 or TCR/SPRG1, and control state.
- `swsusp_arch_suspend()` saves state, makes a small temporary stack adjustment, calls `swsusp_save`, then restores LR.
- `swsusp_arch_resume()` copies restored pages, flushes caches/TLBs where needed, restores timebase and registers, restores MSR/SDR1 or TCR/SPRG1, calls `slb_flush_and_restore_bolted()` on Book3S, then `do_after_copyback()`.

## Control Flow and State
Resume first stops AltiVec streams, copies all pages in `restore_pblist` 8 bytes at a time, performs Book3S cache flush and `tlbia`, restores the saved timebase and GPRs, restores MMU/timer control, optionally invalidates all TLBs on non-Book3S, calls post-copyback C code, restores LR, and returns 0.

## State and Persistence Behavior
The static save area persists CPU state across the restore transition. The routine mutates architectural registers, timebase, MMU state, cache/TLB state, memory image pages, and IOMMU state through `do_after_copyback()`.

## Dependencies and Integration Points
Integrates with generic hibernation page backup lists, Book3S firmware feature checks, SLB restore helpers, `do_after_copyback()` in `swsusp_64.c`, and feature fixups for AltiVec.

## Risks
Ordering is critical: memory copy, cache flush, TLB invalidation, MSR restoration, SLB restore, and IOMMU restore must happen in a valid sequence. The code uses low-level register assumptions and depends on `asm-offsets.h` matching C structures.

## Test Signals
Hibernate/resume on pseries/Book3S hash and radix systems, non-Book3S 64 systems, with IOMMU devices, AltiVec workloads, watchdog enabled, and large restored page lists.
