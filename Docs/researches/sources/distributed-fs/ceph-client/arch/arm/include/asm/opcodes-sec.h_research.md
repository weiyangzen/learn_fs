# sources/distributed-fs/ceph-client/arch/arm/include/asm/opcodes-sec.h

## Purpose
Defines the secure monitor call opcode macro for emitting SMC instructions in either ARM or Thumb-2 code.

## Important APIs, Types, And Functions
Important macros/constants include __ASM_ARM_OPCODES_SEC_H, __SMC(imm4). It depends directly on #include <asm/opcodes.h>.

## Control Flow
__SMC composes the correct ARM/Thumb opcode through opcodes.h instruction-emission helpers.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include #include <asm/opcodes.h>.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
