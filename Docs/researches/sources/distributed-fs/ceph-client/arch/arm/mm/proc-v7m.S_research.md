# sources/distributed-fs/ceph-client/arch/arm/mm/proc-v7m.S

## Purpose
Implements the ARMv7-M and Cortex-M processor backend for no-MMU ARM systems. It supplies minimal processor functions, vector table setup, fault enablement, SVC-based transition setup, optional Cortex-M7/M55 cache handling, and proc-info records for Cortex-M3/M4/M7/M33/M55 plus a generic ARMv7-M match.

## Important APIs, Types, And Functions
Exports `cpu_v7m_proc_init`, `cpu_v7m_proc_fin`, `cpu_v7m_reset`, `cpu_v7m_do_idle`, `cpu_v7m_dcache_clean_area`, `cpu_v7m_switch_mm`, optional suspend/resume stubs, and Cortex-M7 variants `cpu_cm7_dcache_clean_area` and `cpu_cm7_proc_fin`. Setup flows are `__v7m_setup` and `__v7m_cm7_setup`, with `define_processor_functions v7m` and `cm7`.

## Control Flow
Early setup programs SCB VTOR to `vector_table`, enables UsageFault/BusFault/MemManage, lowers SVC and PendSV priorities, temporarily patches the SVC vector, invokes SVC to enter handler mode, restores the vector, sets `control`, optionally invalidates L1 cache for cache-equipped cores, and returns the CCR bits to apply. There is no MMU context switch; `switch_mm` is a return.

## State, Dependencies, And Integration
State is mostly SCB memory-mapped control registers rather than CP15 MMU state: VTOR, SHCSR, SHPR2/3, CCR, and DCCMVAC. It depends on `asm/v7m.h`, `proc-macros.S`, no-MMU abort handlers, `vector_table`, `init_thread_union`, and cache helper `v7m_invalidate_l1`. It integrates through `.proc.info.init` and no-MMU processor functions.

## Risks And Test Signals
Risks include incorrect exception vector patching, stack assumptions during SVC, cache clean ordering on Cortex-M7/M55, and accidentally treating v7-M as MMU capable. Test signals are boot on supported Cortex-M variants, exception entry/return sanity, cache maintenance tests on M7/M55, no-MMU process switching, and WFI idle behavior.
