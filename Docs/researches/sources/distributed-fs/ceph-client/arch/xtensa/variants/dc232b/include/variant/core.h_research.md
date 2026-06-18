# sources/distributed-fs/ceph-client/arch/xtensa/variants/dc232b/include/variant/core.h

## Purpose
This generated header describes the `dc232b` Xtensa core for compile-time kernel configuration.

## Important APIs, types, and functions
It defines a little-endian, windowed, 32-register LX2.1.1 core with density, loops, MAC16, threadptr, CPENABLE/XTIOP, 3-byte maximum instructions, 16 KiB I/D caches with 32-byte writeback lines, XEA2 vectors, and a PTP MMU.

## Control flow
The constants select low-level code for windowed ABI entry, cache/TLB maintenance, timer setup, exception vectors, and instruction decoding. No executable code is defined.

## State and persistence behavior
Hardware state described includes 22 interrupts with 17 external inputs, timers on 6/10/13, NMI on 14, no profiling interrupt macro in the extracted set, VECBASE reset at `0xD0000000`, reset vector at `0xFE000000`, 8 ASID bits, and 4 MMU rings.

## Dependencies and integration points
Kernel Xtensa variant selection pulls this header with the corresponding `tie.h`/`tie-asm.h`. Platform serial and network code use `XCHAL_HAVE_BE`; exception and IRQ code consume the masks and vector addresses.

## Risks and edge cases
The LX2-era 3-byte instruction limit differs from FLIX-capable variants. Interrupt masks differ from `csp`, especially external edge/level allocation. Cache line size is 32 bytes, so using another variant's cache constants would break flush ranges.

## Test signals
Boot and run timer, external IRQ, TLB/page-fault, cache flush, and syscall/exception tests on a `dc232b` build. Confirm code paths do not assume boolean registers or wide instructions.
