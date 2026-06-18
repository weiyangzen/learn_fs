# sources/distributed-fs/ceph-client/arch/arm/include/asm/seccomp.h

## Purpose
Supplies ARM seccomp architecture constants and syscall argument extraction glue.

## Important APIs, Types, And Functions
Important macros/constants include _ASM_SECCOMP_H, SECCOMP_ARCH_NATIVE, SECCOMP_ARCH_NATIVE_NR, SECCOMP_ARCH_NATIVE_NAME. It depends directly on #include <asm-generic/seccomp.h>.

## Control Flow
Seccomp filters observe syscall numbers and arguments from pt_regs through generic seccomp code.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include #include <asm-generic/seccomp.h>.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
