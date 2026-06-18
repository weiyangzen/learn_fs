# sources/distributed-fs/ceph-client/arch/xtensa/variants/csp/include/variant/tie.h

## Purpose
This generated C HAL header describes `csp` TIE and optional-state save-area layout for code that builds register save tables.

## Important APIs, types, and functions
It declares one port coprocessor, CP7 `XTIOP`, with no saved state, `XCHAL_CP_MASK`/`XCHAL_CP_PORT_MASK` as `0x80`, a 36-byte non-coprocessor save area aligned to 4 bytes, and a 48-byte total save area after padding. `XCHAL_NCP_SA_LIST(s)` enumerates nine saved registers: `threadptr`, `acclo`, `acchi`, `br`, `scompare1`, and `m0`-`m3`.

## Control flow
There is no runtime code. Callers define `XCHAL_SA_REG` and expand `XCHAL_NCP_SA_LIST()` or CP lists to generate structs, offsets, unwind metadata, or save/restore code.

## State and persistence behavior
The described state is per-thread optional Xtensa state. `threadptr` is thread-global, MAC16 accumulator and multiplier registers are caller-saved optional state, and `br`/`scompare1` cover boolean and conditional-store options. CP7 exists for I/O port instructions but persists no context bytes.

## Dependencies and integration points
This header must align with `core.h` feature flags and `tie-asm.h` store/load ordering. It is consumed by Xtensa kernel context-switch and user ABI code via variant include paths.

## Risks and edge cases
Changing this generated file without matching the hardware and assembler macros corrupts task state. Save-area padding matters because total size is 48 bytes even though NCP payload is 36 bytes. Direct inclusion is discouraged; it should be reached through the core configuration wrapper.

## Test signals
Compile tests should expand all save-list macros. Runtime signals are stable TLS, MAC16/boolean results across preemption, and no corruption after signal delivery, ptrace, or fork/exec on the `csp` variant.
