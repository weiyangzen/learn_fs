# sources/distributed-fs/ceph-client/arch/xtensa/variants/dc233c/include/variant/core.h

## Purpose
This generated header describes the `dc233c` Xtensa LX4.0.1 core configuration.

## Important APIs, types, and functions
It exports little-endian windowed ABI constants, density/loops/MAC16/threadptr/CPENABLE, no booleans, no FP/DFP/HiFi, 3-byte maximum instructions, 16 KiB I/D writeback caches with 32-byte lines, 22 interrupts, XEA2 vectors, and PTP MMU constants.

## Control flow
No code executes from this file. Compile-time users choose entry, cache, interrupt, MMU, and instruction-decode paths from these macros.

## State and persistence behavior
The described hardware state includes 17 external interrupts, timers on 6/10/13, NMI on 14, VECBASE reset at `0x00002000`, reset vector at `0xFE000000`, user/kernel/double-exception vectors under VECBASE, 8 ASID bits, and 4 rings.

## Dependencies and integration points
This file is selected by the Xtensa variant include path and must match `dc233c` TIE headers. Interrupt definitions feed IRQ setup; cache definitions feed flush/invalidate code; `XCHAL_HAVE_BE` affects platform data endianness.

## Risks and edge cases
The interrupt layout is close to `dc232b` but vector base differs, so sharing assumptions across variants is risky. The lack of booleans means no `BR` save state. Wrong cache geometry breaks DMA/cache coherency.

## Test signals
Build/boot tests should cover timer ticks, external IRQs, page faults, syscall vectors, cache maintenance, and absence of boolean/FP/HiFi paths.
