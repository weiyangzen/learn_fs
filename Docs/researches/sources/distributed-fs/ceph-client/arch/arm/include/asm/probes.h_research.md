# sources/distributed-fs/ceph-client/arch/arm/include/asm/probes.h

## Purpose
Defines ARM kprobe/uprobes instruction-analysis interfaces and architecture-specific probe instruction storage.

## Important APIs, Types, And Functions
Key declarations include typedef u32 probes_opcode_t;; struct arch_probes_insn;; typedef void (probes_insn_handler_t)(probes_opcode_t,; struct arch_probes_insn *,; struct pt_regs *);; typedef unsigned long (probes_check_cc)(unsigned long);. Important macros/constants include _ASM_PROBES_H, MAX_STACK_SIZE.

## Control Flow
Probe setup decodes instruction slots through arch_probes_insn and installs pre/post handlers for breakpoint and single-step emulation.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include the surrounding ARM architecture build and generic kernel headers.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
