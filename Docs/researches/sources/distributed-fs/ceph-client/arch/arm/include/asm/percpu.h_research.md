# sources/distributed-fs/ceph-client/arch/arm/include/asm/percpu.h

## Purpose
Provides ARM per-CPU offset access definitions and falls through to the generic per-CPU implementation.

## Important APIs, Types, And Functions
Key declarations include static inline void set_my_cpu_offset(unsigned long off); extern unsigned int smp_on_up;; unsigned long off;. Important macros/constants include _ASM_ARM_PERCPU_H_, __my_cpu_offset, set_my_cpu_offset(x). It depends directly on #include <asm/insn.h>, #include <asm-generic/percpu.h>.

## Control Flow
Generated code resolves per-CPU variables through the architecture offset mechanism selected by the generic headers.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include #include <asm/insn.h>, #include <asm-generic/percpu.h>.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
