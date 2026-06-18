# sources/distributed-fs/ceph-client/arch/xtensa/variants/test_mmuhifi_c3/include/variant/core.h

## Purpose
This generated Xtensa core-configuration header describes the base ISA, cache, interrupt, exception, debug, and MMU capabilities of the `test_mmuhifi_c3` core. It is a compile-time hardware contract for privileged and non-privileged Xtensa code.

## Important APIs, types, and macros
The header is macro-only. ISA capability flags include windowed registers, density instructions, loops, NSA, min/max, CLAMPS, MUL16, MUL32, S32C1I, release sync, thread pointer, booleans, coprocessor support, and HiFi2 Audio Engine. It describes core geometry through `XCHAL_NUM_AREGS`, instruction size, fetch and data width, write-buffer entries, endian setting, and unaligned access exception behavior. Privileged sections define cache sizes and associativity, interrupt counts and masks, timer interrupt numbers, external interrupt mappings, exception vector virtual and physical addresses, debug level, and MMU properties such as TLB presence, PTP MMU support, ASID bits, and rings.

## Control flow
There is no runtime flow. Conditional compilation is provided by `XTENSA_HAL_NON_PRIVILEGED_ONLY`: privileged cache, interrupt, vector, debug, and MMU details are hidden when non-privileged consumers include the header.

## State and persistence behavior
The file does not store runtime state. It fixes architectural constants that determine kernel memory layout, exception vector placement, cache maintenance behavior, interrupt handling tables, and MMU setup for this variant.

## Dependencies and integration points
The macros integrate with Xtensa arch initialization, cache/TLB code, interrupt controller setup, exception vector assembly, scheduler context management, and HAL code. Several values reference external symbolic constants such as `XTHAL_INTTYPE_*` and `XTHAL_TIMER_UNCONFIGURED`, expected from broader Xtensa HAL headers.

## Risks
Misstated MMU, cache, or vector constants can prevent boot or cause memory corruption. This variant has unaligned load/store exceptions and no hardware unaligned support, so generic code must not assume cheap unaligned access. It has coherent write-back caches and an MMU, which makes cache/TLB maintenance and vector address correctness critical.

## Test signals
Signals include Xtensa kernel builds for `test_mmuhifi_c3`, early boot through exception vector installation, timer interrupt delivery on interrupts 6 and 8, TLB autorefill/page-table tests, cache line size assertions, and runtime tests that exercise S32C1I, thread pointer, boolean registers, and HiFi2 coprocessor state.
