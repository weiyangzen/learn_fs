# sources/distributed-fs/ceph-client/arch/arm/include/asm/opcodes-virt.h

## Purpose
Defines virtualization instruction opcode macros for HVC, ERET, and MSR ELR_hyp in ARM or Thumb-2 mode.

## Important APIs, Types, And Functions
Important macros/constants include __ASM_ARM_OPCODES_VIRT_H, __HVC(imm16), __ERET, __MSR_ELR_HYP(regnum). It depends directly on #include <asm/opcodes.h>.

## Control Flow
Hypervisor stubs use these macros so the assembler receives the right encoding independent of kernel instruction set mode.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include #include <asm/opcodes.h>.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
