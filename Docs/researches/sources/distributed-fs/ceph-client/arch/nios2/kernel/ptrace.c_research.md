# sources/distributed-fs/ceph-client/arch/nios2/kernel/ptrace.c

Purpose: implements Nios II user regsets, ptrace architecture hooks, and syscall trace enter/exit behavior.

Important APIs/types/functions: functions: `Copyright`, `genregs_set`, `ptrace_disable`, `arch_ptrace`, `do_syscall_trace_enter`,
`do_syscall_trace_exit`; prototypes: `membuf_zero`, `user_regset_copyin_ignore`, `ptrace_request`,
`ptrace_report_syscall_exit`; types: `membuf`, `pt_regs`; enums: `nios2_regset`; macros:
`REG_IGNORE_RANGE(START, END)`, `REG_IN_ONE(PTR, LOC)`, `REG_IN_RANGE(PTR, START, END)`.

Control flow: Generic kernel code calls the exported architecture hooks during boot, process management, fault
handling, cache/TLB maintenance, module loading, or platform probing; the file performs the
architecture-specific register and memory operations then returns to the generic subsystem.

State and persistence: State is stored in saved pt_regs/switch_stack frames, user signal frames, debugger register packets,
thread flags, and ptrace-visible register sets.

Dependencies and integration points: Dependencies include `linux/elf.h`, `linux/errno.h`, `linux/kernel.h`, `linux/mm.h`,
`linux/ptrace.h`, `linux/regset.h`, `linux/sched.h`, `linux/sched/task_stack.h`, `linux/uaccess.h`,
`linux/user.h`. Integration points include generic Linux MM, irq, signal, ptrace, module,
timekeeping, devicetree, syscall, and cache/TLB subsystems plus Nios II control-register assembly.
This source is part of the Nios II architecture port under the vendored ceph-client kernel tree.

Risks: Risks include register-frame layout mismatches, incorrect syscall restart/error translation, broken
debugger or signal ABI, recursive exceptions, and returning to userspace with inconsistent status
bits.

Test signals: Test signals are syscall ABI tests, strace/ptrace, signal delivery and sigreturn tests, KGDB
breakpoint handling, interrupt/preemption stress, illegal/alignment exception tests, and user/kernel
register dump sanity.
