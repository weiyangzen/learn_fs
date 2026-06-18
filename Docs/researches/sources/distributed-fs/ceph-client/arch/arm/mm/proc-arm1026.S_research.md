# sources/distributed-fs/ceph-client/arch/arm/mm/proc-arm1026.S

## Purpose
This file implements low-level processor support for ARM1026EJ-S, including ARMv5TEJ/Jazelle capability reporting and CPU-specific cache maintenance.

## Important APIs, Types, and Functions
It defines `cpu_arm1026_*` hooks, `arm1026_*` cache/coherency/DMA helpers, `arm1026_crval`, and `arm1026_processor_functions`. The proc-info entry matches `0x4106a260`, uses `v5t_early_abort` and `legacy_pabort`, and advertises SWP, HALF, THUMB, FAST_MULT, EDSP, and JAVA.

## Control Flow
Setup invalidates caches and TLBs, loads the page-table pointer in MMU builds, optionally disables write-back behavior for write-through configurations, and computes SCTLR bits. Runtime calls use test-clean-invalidate loops for full D-cache operations and direct CP15 operations for TLB/PTE maintenance.

## State and Persistence Behavior
The file persists function/proc metadata in kernel memory and mutates CPU cache, TLB, write-buffer, translation-base, and control-register state during operation.

## Dependencies and Integration Points
It integrates with generic ARM MM, v4 write-back user/cache/TLB tables, abort handling, and `proc-macros.S`. It also depends on configuration options such as `CONFIG_CPU_DCACHE_WRITETHROUGH` and `CONFIG_CPU_CACHE_ROUND_ROBIN`.

## Risks
ARM1026 cache operations differ from the ARM1020 family, so using the wrong table can corrupt coherency. Jazelle/EDSP hwcap reporting must reflect hardware. Loading TTB during setup and context switch must be ordered with TLB/cache invalidation.

## Test Signals
Boot ARM1026EJ-S configurations, validate hwcaps, run process and mmap stress, DMA tests, executable page updates, and write-through/write-back variants. Confirm no stale I-cache after code generation or user-page writes.
