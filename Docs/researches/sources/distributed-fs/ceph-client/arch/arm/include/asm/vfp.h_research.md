# sources/distributed-fs/ceph-client/arch/arm/include/asm/vfp.h

## Purpose
Defines VFP/FPSCR/FPEXC/MVFR bit fields and vfp_disable declaration for ARM floating-point support.

## Important APIs, Types, And Functions
Key declarations include void vfp_disable(void);. Important macros/constants include __ASM_VFP_H, FPSID_IMPLEMENTER_BIT, FPSID_IMPLEMENTER_MASK, FPSID_SOFTWARE, FPSID_FORMAT_BIT, FPSID_FORMAT_MASK, FPSID_NODOUBLE, FPSID_ARCH_BIT, FPSID_ARCH_MASK, FPSID_CPUID_ARCH_MASK.

## Control Flow
VFP exception, context-switch, and feature-detection code decodes CP10/CP11 state using these masks.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include the surrounding ARM architecture build and generic kernel headers.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
