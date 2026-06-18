# sources/distributed-fs/ceph-client/arch/xtensa/variants/test_kc705_be/include/variant/core.h

## Purpose
This generated header describes the big-endian `test_kc705_be` LX6.0.2 Xtensa FPGA test core.

## Important APIs, types, and functions
It defines big-endian windowed ABI, 32 address registers, density, loops, 8-byte max instruction size, MAC16, booleans, threadptr, CPENABLE, HiFi2/HiFi2EP audio support, no FP/DFP, 16 KiB I/D writeback caches with 32-byte lines, 22 interrupts, XEA2 vectors, 8 perf counters, and PTP MMU.

## Control flow
The constants select code paths for big-endian I/O, FLIX-length instruction decode, audio/coprocessor state support, cache/TLB handling, and interrupt/vector setup.

## State and persistence behavior
Hardware state includes CP1 AudioEngineLX and CP7 XTIOP via TIE headers, 16 external interrupts, EXCM level 4, timers on 6/10/13, NMI on 14, profiling interrupt 15, VECBASE reset at `0x00002000`, reset vector at `0xFE000000`, 8 ASID bits, and 4 rings.

## Dependencies and integration points
The paired `tie.h`/`tie-asm.h` define a large AudioEngineLX coprocessor save area. Platform code uses `XCHAL_HAVE_BE` to select big-endian resource behavior.

## Risks and edge cases
This variant has the broadest state footprint in the set: big-endian plus HiFi2/AudioEngine state and 8-byte instructions. Missing coprocessor save/restore corrupts audio registers; wrong endianness breaks MMIO drivers.

## Test signals
Build big-endian KC705, boot with timers/IRQs, run audio/HiFi2 context-switch stress, signal return with coprocessor state, cache/MMU tests, and platform device I/O tests.
