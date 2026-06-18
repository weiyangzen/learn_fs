# sources/distributed-fs/ceph-client/arch/xtensa/variants/test_kc705_hifi/include/variant/core.h

## Purpose
This generated header describes the little-endian `test_kc705_hifi` LX5.0.4 Xtensa FPGA test core.

## Important APIs, types, and functions
It defines windowed ABI, 32 address registers, density, loops, MAC16, booleans, threadptr, CPENABLE, 8-byte max instruction size, HiFi3 support, no FP/DFP, 16 KiB I/D writeback caches with 32-byte lines, 22 interrupts, XEA2 vectors, 8 perf counters, and PTP MMU with 8 ASID bits.

## Control flow
No executable code exists. These macros choose instruction decode, cache, interrupt, vector, MMU, and optional/coprocessor support paths at compile time.

## State and persistence behavior
The hardware description includes 16 external interrupts, EXCM level 3, timers on 6/10/13, NMI on 14, profiling interrupt on 15, VECBASE reset at `0x00002000`, reset vector at `0xFE000000`, 4 MMU rings, and HiFi3-related coprocessor implications handled by this variant's TIE headers outside this work item.

## Dependencies and integration points
The header integrates with Xtensa arch entry, cache/TLB, IRQ, and coprocessor code. It should be read with the corresponding `test_kc705_hifi` `tie.h`/`tie-asm.h` even though only `core.h` is mapped in this item.

## Risks and edge cases
HiFi3 and 8-byte instruction support mean context and instruction-decode paths must not assume base ISA only. Interrupt masks differ slightly from `test_kc705_be` (`INTLEVEL4_MASK` includes `0x9000`), and little-endian platform behavior differs from the BE KC705 variant.

## Test signals
Build and boot this variant, exercise HiFi3/coprocessor context paths, timer and profiling interrupts, NMI, cache/MMU behavior, signal return, and instruction decoding for extended encodings.
