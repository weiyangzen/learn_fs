# sources/distributed-fs/ceph-client/arch/nios2/kernel/traps.c

Purpose: implements Nios II C trap handlers for breakpoints, unaligned access, illegal/supervisor/division
exceptions, unhandled exceptions, and stack/register display.

Important APIs/types/functions: functions: `_send_sig`, `die`, `_exception`, `show_stack`, `breakpoint_c`, `handle_unaligned_c`,
`handle_illegal_c`, `handle_supervisor_instr`, `handle_diverror_c`, `unhandled_exception`,
`handle_trap_1_c`, `handle_trap_2_c`, and 1 more; prototypes: `Copyright`, `make_task_dead`, `die`,
`printk`, `pr_alert`, `_exception`, `pr_emerg`.

Control flow: Generic kernel code calls the exported architecture hooks during boot, process management, fault
handling, cache/TLB maintenance, module loading, or platform probing; the file performs the
architecture-specific register and memory operations then returns to the generic subsystem.

State and persistence: State includes saved exception frames, thread_info flags, interrupt enable masks, current
task/thread pointers, kernel stacks, restart state, and architecture control registers.

Dependencies and integration points: Dependencies include `linux/sched.h`, `linux/sched/debug.h`, `linux/kernel.h`, `linux/signal.h`,
`linux/export.h`, `linux/mm.h`, `linux/ptrace.h`, `asm/traps.h`, `asm/sections.h`,
`linux/uaccess.h`. Integration points include generic Linux MM, irq, signal, ptrace, module,
timekeeping, devicetree, syscall, and cache/TLB subsystems plus Nios II control-register assembly.
This source is part of the Nios II architecture port under the vendored ceph-client kernel tree.

Risks: Risks include register-frame layout mismatches, incorrect syscall restart/error translation, broken
debugger or signal ABI, recursive exceptions, and returning to userspace with inconsistent status
bits.

Test signals: Test signals are syscall ABI tests, strace/ptrace, signal delivery and sigreturn tests, KGDB
breakpoint handling, interrupt/preemption stress, illegal/alignment exception tests, and user/kernel
register dump sanity.
