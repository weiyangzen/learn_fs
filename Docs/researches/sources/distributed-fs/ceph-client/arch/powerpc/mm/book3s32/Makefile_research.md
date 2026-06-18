<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s32/Makefile -->
# sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s32/Makefile

## Purpose
This Makefile selects 32-bit Book3S MMU objects.

## Important APIs, types, and functions
It always builds `mmu.o` and `mmu_context.o`, adds `nohash_low.o` for 603, `hash_low.o` and `tlb.o` for 604-style hash MMUs, and `kuap.o` when KUAP is enabled.

## Control flow
Kbuild conditionals map CPU/MMU feature configs to assembly support files. KASAN builds disable sanitization for `mmu.o` and add `DISABLE_BRANCH_PROFILING`.

## State and persistence behavior
No runtime state; this is build metadata.

## Dependencies and integration points
It integrates Book3S32 hash/nohash MMU code into the PowerPC MM build.

## Risks and edge cases
Instrumentation is deliberately suppressed for early/low-level MMU code; changing that can break boot or real-mode paths.

## Test signals
Successful builds for 603, 604, KUAP, and KASAN combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s32/Makefile -->
