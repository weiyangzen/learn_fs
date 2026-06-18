# sources/distributed-fs/ceph-client/arch/nios2/kernel/entry.S

Purpose: implements Nios II exception, interrupt, syscall, signal-return, context-switch, and kuser helper
assembly entry paths.

Important APIs/types/functions: entry points: `inthandler`, `handle_trap`, `handle_system_call`, `ret_from_interrupt`, `sys_clone`,
`__sys_clone3`, `sys_rt_sigreturn`, `resume`, `ret_from_fork`, `ret_from_kernel_thread`; prototypes:
`Copyright`.

Control flow: Exceptions enter through `inthandler`, save pt_regs, clear exception-mode state, dispatch through
exception/trap tables, run syscalls or C exception handlers, process return-to-user work, and
finally restore registers with `eret`.

State and persistence: State includes saved exception frames, thread_info flags, interrupt enable masks, current
task/thread pointers, kernel stacks, restart state, and architecture control registers.

Dependencies and integration points: Dependencies include `linux/sys.h`, `linux/linkage.h`, `asm/asm-offsets.h`, `asm/asm-macros.h`,
`asm/thread_info.h`, `asm/errno.h`, `asm/setup.h`, `asm/entry.h`, `asm/unistd.h`, `asm/processor.h`.
Integration points include generic Linux MM, irq, signal, ptrace, module, timekeeping, devicetree,
syscall, and cache/TLB subsystems plus Nios II control-register assembly. This source is part of the
Nios II architecture port under the vendored ceph-client kernel tree.

Risks: Risks include register-frame layout mismatches, incorrect syscall restart/error translation, broken
debugger or signal ABI, recursive exceptions, and returning to userspace with inconsistent status
bits.

Test signals: Test signals are syscall ABI tests, strace/ptrace, signal delivery and sigreturn tests, KGDB
breakpoint handling, interrupt/preemption stress, illegal/alignment exception tests, and user/kernel
register dump sanity.
