# sources/distributed-fs/ceph-client/arch/arm/mm/proc-fa526.S

## Purpose
This file implements low-level MMU/cache/TLB support for the Faraday FA526 core.

## Important APIs, Types, and Functions
It defines `cpu_fa526_proc_init/fin/reset/do_idle/dcache_clean_area/switch_mm/set_pte_ext`, `fa526_cr1_clear`, `fa526_cr1_set`, and `fa526_processor_functions`. The proc-info entry matches `0x66015261` masked by `0xff01fff1`, uses `v4_early_abort` and `legacy_pabort`, and advertises SWP and HALF.

## Control Flow
Setup invalidates caches/TLBs, reads CP15 control, applies clear/set masks, and returns to early boot. Runtime context switch and PTE paths use ARMv3-style PTE translation plus D-cache clean/write-buffer drain.

## State and Persistence Behavior
The file mutates CP15 control, cache, TLB, page-table base, and hardware PTE state. It stores static proc/function metadata.

## Dependencies and Integration Points
It depends on FA526 CP15 behavior, ARMv4-style page tables, `proc-macros.S`, abort handlers, and generic MM cache/TLB APIs.

## Risks
The reset path notes a TODO around CP8 and may not use all available reset mechanisms. FA526-specific control masks and cache behavior must not be mixed with ARM9/ARM10 files. Incorrect PTE clean ordering can cause stale translations.

## Test Signals
Boot FA526 hardware, run fork/exec/mmap, page-fault, DMA, and cache coherency tests. Verify CPU ID match and reset behavior.
