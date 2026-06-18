# sources/distributed-fs/ceph-client/arch/arm/include/asm/uprobes.h

## Purpose
Defines ARM uprobes breakpoint opcodes, XOL slot size, per-task saved trap state, and arch_uprobe handler hooks.

## Important APIs, Types, And Functions
Key declarations include typedef u32 uprobe_opcode_t;; struct arch_uprobe_task {; unsigned long saved_trap_no;; struct arch_uprobe {; unsigned long ixol[2];; void (*prehandler)(struct arch_uprobe *auprobe,. Important macros/constants include _ASM_UPROBES_H, MAX_UINSN_BYTES, UPROBE_XOL_SLOT_BYTES, UPROBE_SWBP_ARM_INSN, UPROBE_SS_ARM_INSN, UPROBE_SWBP_INSN, UPROBE_SWBP_INSN_SIZE. It depends directly on #include <asm/probes.h>, #include <asm/opcodes.h>.

## Control Flow
Uprobe installation copies and decodes target instructions, replaces them with the ARM breakpoint opcode, and emulates/single-steps through pre/post handlers.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include #include <asm/probes.h>, #include <asm/opcodes.h>.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
