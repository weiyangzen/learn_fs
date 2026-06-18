# sources/distributed-fs/ceph-client/arch/arm/mm/proc-arm720.S

## Purpose
This file supports ARM710/ARM720T-class MMU processors with writethrough IDC cache behavior.

## Important APIs, Types, and Functions
It defines `cpu_arm720_dcache_clean_area`, `proc_init`, `proc_fin`, `do_idle`, `switch_mm`, `set_pte_ext`, and `reset`. It includes separate setup data for ARM710 and ARM720, `arm720_crval`, a proc-info macro, and `arm720_processor_functions` with `v4t_late_abort` and `legacy_pabort`.

## Control Flow
CPU probe selects one of the generated proc-info records, calls the appropriate setup routine to invalidate caches/TLBs and compute control-register bits, then installs the function table. `switch_mm()` invalidates cache, updates CP15 c2 with the new page table, and flushes TLBs.

## State and Persistence Behavior
The file mutates CP15 control, cache, TLB, and TTB state. It stores only static proc-info metadata.

## Dependencies and Integration Points
It depends on ARMv4T CP15 instructions, the generic processor-function table format, v4 cache/TLB helper tables, and ARM page-table macros. It integrates with legacy ARM MMU boot and context switching.

## Risks
The cache is assumed writethrough, so D-cache clean hooks are mostly no-op. If a variant behaves differently, DMA and page-table coherency can fail. ARM710 and ARM720 control bits are distinct and must remain tied to the right proc-info.

## Test Signals
Build ARM710/720 configs, boot legacy boards, run fork/exec and mmap tests, exercise TLB shootdown and context switching, and verify user/kernel cache flush APIs do not leave stale instructions.
