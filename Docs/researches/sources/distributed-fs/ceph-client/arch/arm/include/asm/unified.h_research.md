# sources/distributed-fs/ceph-client/arch/arm/include/asm/unified.h

## Purpose
Provides assembler compatibility macros for unified ARM/Thumb syntax.

## Important APIs, Types, And Functions
Important macros/constants include __ASM_UNIFIED_H, AR_CLASS(x...), M_CLASS(x...), AR_CLASS(x...), M_CLASS(x...), PSR_ISETSTATE, ARM(x...), THUMB(x...), W(instr), WASM(instr).

## Control Flow
Assembly headers include it so macros assemble correctly across ARM and Thumb-2 kernel builds.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include the surrounding ARM architecture build and generic kernel headers.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
