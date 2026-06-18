# sources/distributed-fs/ceph-client/arch/arm/mm/proc-arm1020e.S

## Purpose
This file provides ARM1020E/ARM1020TE low-level processor hooks, extending the ARM1020-style implementation for ARMv5TE capability and control-register differences.

## Important APIs, Types, and Functions
It defines the `cpu_arm1020e_*` function family for init, finish, reset, idle, D-cache clean, MM switch, and PTE updates; `arm1020e_*` cache, coherency, and DMA helpers; `arm1020e_crval`; and `arm1020e_processor_functions`. The proc-info entry matches CPUID `0x4105a200`, uses ARMv5TE naming, and advertises `HWCAP_EDSP` in addition to SWP, HALF, and THUMB.

## Control Flow
CPU probe selects `__arm1020e_proc_info`, then `__arm1020e_setup()` invalidates caches/TLBs and computes desired SCTLR bits. The installed function table handles all later cache, TLB, page-table, and reset operations through indirect calls.

## State and Persistence Behavior
Runtime state is CP15 and cache/TLB/PTE state only. Static proc-info and function tables persist in kernel memory.

## Dependencies and Integration Points
The file integrates with the ARM CPU probe path, v4 write-back cache and TLB tables, `legacy_pabort`, `v4t_early_abort`, and the generic MM/page-table code via `set_pte_ext()` and `switch_mm()`.

## Risks
The ARM1020E control mask differs from ARM1020; copying values between files can leave stale SCTLR bits set. Cache-range code depends on 32-byte lines and 16 segments. DMA maintenance must match write-back/write-through configuration.

## Test Signals
Boot ARM1020E builds, confirm the CPU name and EDSP hwcap, stress context switches, page faults, DMA map/unmap operations, and executable mapping updates. Compare behavior under `CONFIG_CPU_DCACHE_WRITETHROUGH` and write-back builds.
