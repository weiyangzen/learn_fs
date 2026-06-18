# sources/distributed-fs/ceph-client/arch/xtensa/variants/fsf/include/variant/core.h

## Purpose
This generated header describes the `fsf` Xtensa LX2.0.0 core configuration.

## Important APIs, types, and functions
It defines a big-endian, windowed core with 64 address registers, density and loops, no MUL32/MAC16/CP/booleans, threadptr support in `core.h`, 3-byte max instructions, 8 KiB I/D caches with 16-byte lines, non-writeback D-cache, 17 interrupts, and PTP MMU with 8 ASID bits.

## Control flow
The macros select compile-time Xtensa entry/cache/MMU behavior. No functions are defined.

## State and persistence behavior
The hardware description includes 10 external interrupts, 4 interrupt levels, EXCM level 1, timers on interrupts 10/11/12, no NMI, reset vector `0xFE000020`, user/kernel/double-exception vectors near `0xD0000200`, and 4 MMU rings.

## Dependencies and integration points
`XCHAL_HAVE_BE` drives big-endian platform choices such as serial I/O type and Ethernet platform data. Cache and interrupt constants feed core arch code. The paired TIE headers oddly describe no saved state despite core threadptr support.

## Risks and edge cases
Big-endian operation, 64 physical address registers, no MAC16/MUL32, no NMI, and 16-byte cache lines distinguish this variant sharply from the others. The threadptr/core-vs-tie discrepancy should be treated carefully by TLS/context-switch code.

## Test signals
Build big-endian Xtensa, run IRQ/timer tests, cache flush tests with 16-byte lines and non-writeback D-cache, syscall/exception vectors, and TLS tests to confirm thread pointer handling.
