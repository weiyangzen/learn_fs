<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/entry.S -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/entry.S

Purpose: implements SH-2A exception, interrupt, and syscall entry.

Important APIs/types/functions: `exception_handler`, `interrupt_entry`, `trap_entry`, BIOS handler path, movmu/movml frame save logic.

Control flow: uses SH-2A instructions to save registers, manage SR.MD/kernel stack switching, dispatch interrupt/trap/exception vectors, and return through common paths.

State and persistence: state is pt_regs, CPU mode byte, thread-info stack pointer, SR/PR/GBR/MAC registers.

Dependencies/integration: depends on asm offsets, SH-2A exception vector table, `do_IRQ`, syscall entry, and trap table.

Risks: SH-2A compact save/restore instructions make offset accuracy critical.

Test signals: test interrupts, syscalls, branch-delay traps, ptrace, and signal frames on SH-2A.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/entry.S -->
