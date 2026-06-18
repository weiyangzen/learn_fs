# sources/distributed-fs/ceph-client/arch/arm/mm/proc-mohawk.S

## Purpose
This file implements low-level support for Marvell PJ1/Mohawk 88SV331x cores, described as a hybrid of XScale3 and Marvell core behavior.

## Important APIs, Types, and Functions
It defines `cpu_mohawk_*` init/finish/reset/idle/dcache/switch-mm/set-PTE/suspend/resume hooks, `mohawk_*` cache/coherency/DMA helpers, `mohawk_crval`, and `mohawk_processor_functions`. `__88sv331x_proc_info` matches CPUID `0x56158000` masked by `0xfffff000` and advertises ARMv5TE features.

## Control Flow
Setup invalidates caches/TLBs, computes SCTLR bits, and returns to boot. Runtime cache and DMA paths use 32-byte cache-line loops. `switch_mm()` performs cache/TLB maintenance around TTB changes. Suspend/resume saves/restores CP15 state.

## State and Persistence Behavior
The file changes cache, TLB, TTB, control-register, and PTE state and stores static CPU metadata. Suspend snapshots persist in caller-provided memory.

## Dependencies and Integration Points
It depends on XScale-like PTE/cache behavior, ARMv5TE helper tables, abort handling, CPU suspend, and generic ARM cache/DMA APIs.

## Risks
Hybrid core behavior makes copying from either XScale or Feroceon risky. Control-register clear/set masks, PTE format, and cache maintenance must stay Mohawk-specific. CPUID matching is narrow and should not collide with other Marvell cores.

## Test Signals
Boot 88SV331x/PJ1 systems, run DMA and executable-coherency tests, stress process switching and PTE updates, and validate suspend/resume. Check CPU identification and hwcap output.
