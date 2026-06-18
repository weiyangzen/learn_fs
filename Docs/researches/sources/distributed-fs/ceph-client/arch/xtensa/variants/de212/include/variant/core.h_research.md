# sources/distributed-fs/ceph-client/arch/xtensa/variants/de212/include/variant/core.h

## Purpose
This generated header describes the `de212` LX6.0.2 Xtensa core configuration.

## Important APIs, types, and functions
It defines a little-endian, windowed, 32-register core with density, loops, MAC16, no threadptr, no CPENABLE, no booleans, no FP/HiFi, 3-byte max instructions, 8 KiB I/D writeback caches with 32-byte lines, and a reduced MMU configuration.

## Control flow
The macros drive compile-time selection for exception vectors, timers, cache code, and whether coprocessor/threadptr paths exist.

## State and persistence behavior
Hardware state includes 22 interrupts, 17 external inputs, timers on 6/10/13, NMI on 14, no profiling interrupt, VECBASE reset at `0x60000000`, reset vector at `0x50000000`, zero perf counters, `XCHAL_HAVE_PTP_MMU` 0, zero ASID bits, and one ring.

## Dependencies and integration points
This variant is paired with `de212` TIE headers that save only MAC16 and `SCOMPARE1` optional state. MMU and privilege code must honor the lack of PTP MMU/ASIDs despite `XCHAL_HAVE_TLBS` being set.

## Risks and edge cases
Code that assumes `THREADPTR`, CPENABLE, ASIDs, performance counters, or full PTP MMU will fail. The unusual reset/vector addresses must match the board or simulator memory map. Cache size is smaller than most neighboring variants.

## Test signals
Build and boot with this variant, checking exception vectors, timer interrupts, cache maintenance, TLB behavior without PTP MMU, no TLS-register assumptions, and no coprocessor enable paths.
