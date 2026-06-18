# sources/distributed-fs/ceph-client/arch/arm/mm/proc-v7.S

## Purpose
Provides the ARMv7-A/R processor backend used by the 32-bit ARM kernel MM layer. It defines low-level processor operations for init/finalize, reset, idle, D-cache cleaning, context switch, PTE writes through included 2-level or LPAE helpers, suspend/resume, CPU errata setup, and `proc_info_list` records for Cortex, Krait, Brahma, and PJ4B cores.

## Important APIs, Types, And Functions
Exports `cpu_v7_proc_init`, `cpu_v7_proc_fin`, `cpu_v7_reset`, `cpu_v7_do_idle`, `cpu_v7_dcache_clean_area`, branch predictor hardening switch variants, `cpu_v7_do_suspend`, `cpu_v7_do_resume`, Cortex-A9/PJ4B-specific suspend hooks, and setup labels such as `__v7_setup`, `__v7_ca9mp_setup`, and `__v7_pj4b_setup`. `define_processor_functions` emits the `struct processor` tables consumed by ARM proc selection.

## Control Flow
Early boot matches MIDR against `.proc.info.init` entries, jumps through the selected `initfn`, invalidates L1 caches, applies errata by CPU part/revision, programs TTBCR/TTBRs, PRRR/NMRR, ThumbEE state, and returns the SCTLR value to `head.S`. Runtime calls enter the function table for idle, reset, `switch_mm`, PTE updates, and suspend/resume. Hardened branch predictor variants wrap `switch_mm` with SMC/HVC, ICIALLU, or BPIALL sequences depending on configuration and CPU family.

## State, Dependencies, And Integration
Persistent state is architectural CP15 state: SCTLR, ACTLR, TTB registers, domain register, PRRR/NMRR, CPACR, context/thread IDs, and CPU-specific diagnostic registers. It depends on `proc-macros.S`, `proc-v7-2level.S` or `proc-v7-3level.S`, alternative patching macros, `asm/pgtable-hwdef.h`, SMCCC constants, and suspend code in the ARM core. Integration points are `proc_info_list`, `v7wbi_tlb_fns`, `v6_user_fns`, cache function tables, CPU suspend, PSCI, and branch predictor hardening.

## Risks And Test Signals
Risks are wrong errata gating, missing barriers around TLB/cache invalidation, incorrect LPAE vs non-LPAE TTBR setup, suspend state size mismatches, and hardening variant mismatch for vulnerable CPUs. Test signals include boot on each matched CPU class, SMP/UP alternative patching, context switch stress, suspend/resume, page-table permission tests, KPTI/speculation-hardening coverage, and kernel selftests that exercise mapping changes and signal delivery.
