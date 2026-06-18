# sources/distributed-fs/ceph-client/arch/xtensa/variants/csp/include/variant/core.h

## Purpose
This generated Xtensa HAL header describes the `csp`/`xt_lnx` core configuration consumed by kernel assembly, cache, MMU, exception, and interrupt code.

## Important APIs, types, and functions
The file exports only preprocessor constants. Key groups define ISA features (`XCHAL_HAVE_WINDOWED`, density, loops, MAC16, booleans, threadptr, coprocessor support), cache geometry, interrupt masks and types, vector addresses, debug/TRAX support, performance counters, and MMU capability.

## Control flow
There is no runtime control flow. Inclusion selects compile-time code paths in Xtensa low-level code: windowed register spilling, instruction decoding up to 8 bytes, writeback cache maintenance, XEA2 vector placement, timer interrupt selection, and page-table MMU handling.

## State and persistence behavior
No state is stored here. The constants must match the synthesized core: little-endian, 32 address registers, 64 KiB I-cache, 16 KiB D-cache, 64-byte lines, writeback D-cache, 22 interrupts, three timers on interrupts 6/10/13, NMI on 14, profiling on 15, 8 perf counters, PTP MMU with 8 ASID bits and 4 rings.

## Dependencies and integration points
The header is pulled through Xtensa variant include paths and is paired with this variant's `tie.h` and `tie-asm.h`. It supplies `XCHAL_HAVE_BE` to platform code, cache constants to cacheflush/TLB code, and interrupt/vector constants to entry code.

## Risks and edge cases
Any mismatch with hardware can break exception entry, timer delivery, cache maintenance, or user/kernel address translation. The 8-byte max instruction size requires decode paths to handle FLIX-length tables. Non-coherent writeback cache settings require correct DMA/cache synchronization elsewhere.

## Test signals
Build an Xtensa `csp` configuration and boot to user space. Exercise timer ticks, external interrupts, NMI/debug vectors, page faults, cache flush paths, performance counters, and endianness-sensitive platform drivers.
