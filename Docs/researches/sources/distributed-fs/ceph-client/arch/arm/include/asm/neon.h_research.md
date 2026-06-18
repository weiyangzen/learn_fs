# sources/distributed-fs/ceph-client/arch/arm/include/asm/neon.h

## Purpose
Defines kernel NEON availability and critical-section entry/exit helpers for code that temporarily uses NEON/VFP registers in kernel mode.

## Important APIs, Types, And Functions
Key declarations include void kernel_neon_begin(void);; void kernel_neon_end(void);. Important macros/constants include cpu_has_neon(), kernel_neon_begin(). It depends directly on #include <asm/hwcap.h>.

## Control Flow
Callers test cpu_has_neon, enter kernel_neon_begin, perform bounded SIMD work with preemption/FPU ownership handled elsewhere, and leave through kernel_neon_end.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include #include <asm/hwcap.h>.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
