# sources/distributed-fs/ceph-client/arch/arm/mm/proc-arm1020.S

## Purpose
This assembly file supplies low-level MMU, cache, TLB, reset, idle, DMA, and PTE hooks for ARM1020T processors.

## Important APIs, Types, and Functions
It defines `cpu_arm1020_proc_init/fin/reset/do_idle/dcache_clean_area/switch_mm/set_pte_ext`, cache hooks such as `arm1020_flush_icache_all`, `arm1020_flush_user_cache_range`, coherency helpers, and DMA range helpers. It uses `armv3_set_pte_ext` from `proc-macros.S`, defines `arm1020_crval`, and publishes `arm1020_processor_functions` with `dabort=v4t_early_abort` and `pabort=legacy_pabort`. `__arm1020_proc_info` matches CPUID `0x4104a200` masked by `0xff0ffff0` and advertises ARMv5T capabilities.

## Control Flow
Boot CPU probing matches `__arm1020_proc_info`, calls `__arm1020_setup()` to invalidate caches/TLBs and compute SCTLR bits, then installs the processor function and cache/TLB/user tables. Runtime control flows through indirect function tables for cache flushes, DMA maintenance, `switch_mm()`, and PTE installation.

## State and Persistence Behavior
The file mutates CP15 control, cache, TLB, domain/translation base, and hardware PTE state. The processor-function table and proc-info records are static kernel metadata. There is no disk persistence.

## Dependencies and Integration Points
It depends on ARMv4/v5 CP15 operations, ARM page-table bit definitions, generic abort handlers, `proc-macros.S`, v4 WB cache/TLB helper tables, and the architecture CPU probe path.

## Risks
Cache geometry constants drive whole-cache loops and must match the core. PTE translation must maintain Linux/hardware PTE coherency. `switch_mm()` flushes caches/TLBs broadly, so missing barriers or D-cache cleans can cause stale page tables. Incorrect CPUID masks can bind the wrong low-level hooks.

## Test Signals
Build `CONFIG_CPU_ARM1020` kernels, boot on matching hardware or emulator, run fork/exec/mmap stress, module and DMA tests, instruction-cache coherency tests, and soft-reset/kexec paths. Check CPU name/capability strings and absence of data aborts during page-table churn.
