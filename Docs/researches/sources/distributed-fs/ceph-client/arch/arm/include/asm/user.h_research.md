# sources/distributed-fs/ceph-client/arch/arm/include/asm/user.h

## Purpose
Defines legacy ARM user core-dump structures, including general register, FPA, VFP, and VFP exception state layouts visible to debuggers.

## Important APIs, Types, And Functions
Key declarations include struct user_fp {; struct fp_reg {; unsigned int sign1:1;; unsigned int unused:15;; unsigned int sign2:1;; unsigned int exponent:14;. Important macros/constants include _ARM_USER_H. It depends directly on #include <asm/page.h>, #include <asm/ptrace.h>.

## Control Flow
Core dump and ptrace consumers read these structures to interpret saved user CPU and floating-point state.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include #include <asm/page.h>, #include <asm/ptrace.h>.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
