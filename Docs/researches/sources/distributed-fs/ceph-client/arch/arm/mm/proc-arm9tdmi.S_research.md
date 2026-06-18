# sources/distributed-fs/ceph-client/arch/arm/mm/proc-arm9tdmi.S

## Purpose
This file provides minimal no-MMU processor support for ARM9TDMI and P2001 cores.

## Important APIs, Types, and Functions
All `cpu_arm9tdmi_*` hooks are no-op returns except reset, which branches to the supplied reset address. `define_processor_functions arm9tdmi` is marked `nommu=1` with `nommu_early_abort` and `legacy_pabort`. The proc-info macro emits entries for ARM9TDMI and P2001, advertising SWP, THUMB, and 26-bit capability.

## Control Flow
CPU probe matches one of the proc-info records. Setup returns immediately, and runtime memory-management calls do not perform cache/TLB work because this path has no MMU surface.

## State and Persistence Behavior
No mutable CPU memory-management state is programmed. Static proc-info records persist in kernel memory.

## Dependencies and Integration Points
It integrates with no-MMU ARM boot, CPU probe, generic cache function selection (`v4_cache_fns`), and legacy abort handling.

## Risks
Selecting this no-op implementation for a CPU with real cache/protection requirements would break coherency. CPUID mask overlap and 26-bit capability reporting are the main metadata risks.

## Test Signals
Build ARM9TDMI/P2001 no-MMU configs, validate boot, exception handling, CPU identification, THUMB operation, and reset vector transfer.
