# sources/distributed-fs/ceph-client/arch/arm/mm/proc.c

## Purpose
Declares C prototypes and emits `__ADDRESSABLE()` references for low-level ARM processor assembly routines that are called from C but do not have native C definitions. This supports CFI and prevents referenced assembly entry points from being discarded or considered type-missing.

## Important APIs, Types, And Functions
Contains configuration-gated declarations for `cpu_*_proc_init`, `proc_fin`, `reset`, `do_idle`, `dcache_clean_area`, `switch_mm`, `set_pte_ext`, and suspend/resume functions across ARM7/9/10, SA110, XScale, XSC3, Mohawk, Feroceon, v6, v7, and v7-M. It uses `__ADDRESSABLE(symbol)` for each function.

## Control Flow
There is no runtime control flow beyond static references. The preprocessor selects declarations matching enabled CPU families. The function order mirrors `struct processor`, helping CFI see the same callable signatures that the assembly function table exposes.

## State, Dependencies, And Integration
No persistent state is owned. Dependencies are `asm/proc-fns.h`, CPU Kconfig symbols, `phys_addr_t`, `struct mm_struct`, and `pte_t`. Integration is with low-level assembly files under `arch/arm/mm`, CFI, linker reachability, and indirect calls through processor tables.

## Risks And Test Signals
Risks are signature drift between C declarations, `struct processor`, and assembly implementations, especially LPAE `set_pte_ext` arity or reset argument shape. Test signals are CFI-enabled builds for each CPU family, allmodconfig/allyesconfig compile coverage, and boot-time indirect calls through selected processor functions.
