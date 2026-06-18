# sources/distributed-fs/ceph-client/arch/arm/mm/proc-sa110.S

## Purpose
This file provides low-level MMU/cache support for StrongARM SA-110.

## Important APIs, Types, and Functions
It defines `cpu_sa110_proc_init`, `proc_fin`, `reset`, `do_idle`, `dcache_clean_area`, `switch_mm`, `set_pte_ext`, `sa110_crval`, and `sa110_processor_functions`. The proc-info entry matches `0x4401a100`, uses `v4_early_abort` and `legacy_pabort`, and advertises SWP, HALF, 26BIT, and FAST_MULT.

## Control Flow
Setup invalidates cache/TLB state and computes control bits. Idle loads from an uncacheable address to enter low-power behavior. Context switch writes the TTB and flushes TLB/cache state. PTE installation uses ARMv3 translation and cache cleaning.

## State and Persistence Behavior
The file changes CP15 control, cache, TLB, TTB, and PTE state. Static CPU metadata remains in kernel sections.

## Dependencies and Integration Points
It depends on StrongARM CP15 behavior, an `UNCACHEABLE_ADDR` idle mechanism, ARMv4 page-table format, and generic ARM MM/cache APIs.

## Risks
SA-110 idle is hardware-specific and depends on an uncacheable access. 26-bit capability metadata is legacy-sensitive. Cache line size and control masks must match SA-110 exactly.

## Test Signals
Boot SA-110 platforms, verify idle wakeup, process switching, DMA/cache coherency, page faults, and reset. Confirm `/proc/cpuinfo` style capabilities match expectations.
