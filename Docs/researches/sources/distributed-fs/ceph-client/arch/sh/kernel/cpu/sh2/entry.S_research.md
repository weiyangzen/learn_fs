<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2/entry.S -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2/entry.S

Purpose: implements SH-2 exception, interrupt, and trap entry.

Important APIs/types/functions: `exception_handler`, `interrupt_entry`, `trap_entry`, `restore_all`, BIOS handler paths, stack offset constants.

Control flow: saves interrupted registers, switches from user to kernel stack when needed, dispatches vectors <31 to exception table, >=64 to `do_IRQ`, and trap range to syscall handling, then returns through common ret paths.

State and persistence: state is pt_regs frame, per-CPU mode/thread-info variables, SR.MD, PR/GBR/MAC registers.

Dependencies/integration: depends on generated asm offsets, entry macros, syscall and IRQ common code, SMP cpuid support.

Risks: frame layout must match C `pt_regs`; any stack arithmetic bug corrupts returns or ptrace/signal state.

Test signals: run syscall, IRQ, nested exception, ptrace, and user/kernel trap tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2/entry.S -->
