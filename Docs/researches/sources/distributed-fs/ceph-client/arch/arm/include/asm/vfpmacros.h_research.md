# sources/distributed-fs/ceph-client/arch/arm/include/asm/vfpmacros.h

## Purpose
Provides assembly macros for moving VFP system registers and saving/restoring VFP register banks.

## Important APIs, Types, And Functions
Assembly macros include .macro VFPFMRX, rd, sysreg, cond, .macro VFPFMXR, sysreg, rd, cond, .macro VFPFLDMIA, base, tmp, .macro VFPFSTMIA, base, tmp. It depends directly on #include <asm/hwcap.h>, #include <asm/vfp.h>.

## Control Flow
Low-level VFP context-switch code expands VFPFMRX/VFPFMXR and FLDMIA/FSTMIA sequences with CPU-specific register counts.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include #include <asm/hwcap.h>, #include <asm/vfp.h>.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
