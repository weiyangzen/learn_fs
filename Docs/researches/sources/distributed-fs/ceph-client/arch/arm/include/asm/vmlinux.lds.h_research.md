# sources/distributed-fs/ceph-client/arch/arm/include/asm/vmlinux.lds.h

## Purpose
Defines ARM linker-script macros for CPU/init/MMU section retention, proc_info, idmap text, unwind sections, exception vectors overlays, stubs, assertions, and TCM placement.

## Important APIs, Types, And Functions
Important macros/constants include ARM_CPU_DISCARD(x), ARM_CPU_KEEP(x), ARM_CPU_DISCARD(x), ARM_CPU_KEEP(x), ARM_EXIT_KEEP(x), ARM_EXIT_DISCARD(x), ARM_EXIT_KEEP(x), ARM_EXIT_DISCARD(x), ARM_MMU_KEEP(x), ARM_MMU_DISCARD(x). It depends directly on #include <asm-generic/vmlinux.lds.h>.

## Control Flow
The vmlinux linker script expands these macros to keep or discard sections based on configuration, place vectors at 0xffff0000 overlays, expose LMA symbols, and verify size/alignment constraints.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include #include <asm-generic/vmlinux.lds.h>.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
