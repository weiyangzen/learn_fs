# sources/distributed-fs/ceph-client/arch/arm/mm/proc-macros.S

## Purpose
This shared assembly include defines macros used by ARM processor support files. It centralizes access to common kernel structure offsets, ASID extraction, control-register value selection, cache-line-size decoding, Linux-to-hardware PTE translation, processor-function table construction, and MPU protection-region value generation.

## Important APIs, Types, and Functions
Key macros include `vma_vm_mm`, `vma_vm_flags`, `act_mm`, `mmid`, `asid`, `crval`, `dcache_line_size`, `icache_line_size`, `armv6_mt_table`, `armv6_set_pte_ext`, `armv3_set_pte_ext`, `xscale_set_pte_ext_prologue`, `xscale_set_pte_ext_epilogue`, `define_processor_functions`, `globl_equ`, `initfn`, `pr_sz`, and `pr_val`.

`define_processor_functions` emits the table consumed through `struct processor`, including data abort, prefetch abort, init, bugs, finish, reset, idle, D-cache clean, switch-mm, set-PTE, and optional suspend/resume entries.

## Control Flow
This file has no standalone execution. Including assembly files expand these macros into actual CPU-specific functions or tables. The PTE macros implement the branch-heavy Linux PTE to hardware descriptor translation used by several CPU files.

## State and Persistence Behavior
It creates no state directly, but macro expansion writes persistent `.proc.info.init`, `__INITDATA`, or `.rodata` function tables and generates instructions that mutate page tables and cache state.

## Dependencies and Integration Points
It depends on `asm-offsets.h`, page-table bit definitions, thread/task offsets, and V7-M constants when configured. Every proc file in this work item depends on it for table layout or PTE/control-register helpers.

## Risks
This is a high-blast-radius file. A bit-layout change can break many CPU families. The sanity checks around Linux PTE bits protect assumptions but only for compile-time constants. Table ordering in `define_processor_functions` must match C declarations in `<asm/proc-fns.h>`.

## Test Signals
Build a matrix of ARMv3/v4/v5/v6/v7, MMU/no-MMU, LPAE/non-LPAE, SMP/UP, and big-endian/little-endian configurations. Runtime tests should stress `set_pte_ext()`, context switching, cache flushes, suspend/resume table entries, and CPU probing for every proc file using these macros.
