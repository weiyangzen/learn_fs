# sources/distributed-fs/ceph-client/arch/arm/mm/proc-arm920.S

## Purpose
This file implements MMU, cache, DMA, context-switch, and suspend/resume hooks for ARM920T.

## Important APIs, Types, and Functions
It defines `cpu_arm920_*` hooks, `arm920_*` cache/coherency/DMA helpers, `cpu_arm920_do_suspend()`, `cpu_arm920_do_resume()`, `arm920_crval`, and `arm920_processor_functions` with suspend support. The proc-info entry matches `0x41009200`, advertises ARMv4T SWP/HALF/THUMB, and chooses `arm920_cache_fns` or `v4wt_cache_fns` depending on D-cache mode.

## Control Flow
Setup invalidates caches/TLBs and computes control bits. Cache operations either walk cache index geometry or use write-through helper paths. `switch_mm()` cleans/invalidates caches, loads CP15 c2, and invalidates TLBs. Suspend saves PID/domain/control registers; resume restores them and branches to `cpu_resume_mmu`.

## State and Persistence Behavior
The file mutates CPU control, cache, TLB, TTB, PID/domain, and PTE state. Suspend buffers supplied by callers persist a small CP15 register snapshot.

## Dependencies and Integration Points
It depends on v4 MMU/TLB/cache helper tables, generic CPU suspend, `legacy_pabort`, `v4t_early_abort`, and ARM page-table macros. It integrates with S3C24xx-style sleep support and generic ARM MM.

## Risks
Cache geometry constants and write-through conditionals must match hardware. Suspend/resume must restore CP15 state in the right order or resume with invalid mappings. Whole-cache flushes are broad and can hide performance regressions.

## Test Signals
Boot ARM920T boards, run suspend/resume, DMA, fork/exec, mmap, module, and executable-page coherency tests. Verify both write-back and write-through builds if supported.
