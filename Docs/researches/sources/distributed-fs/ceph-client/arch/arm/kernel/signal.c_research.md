# sources/distributed-fs/ceph-client/arch/arm/kernel/signal.c

Purpose: implements ARM signal delivery and return ABI, including legacy and realtime frames, VFP/iWMMXt auxiliary contexts, syscall restart handling, randomized sigreturn page content, and return-to-user pending work.

Important APIs/types/functions: `sys_sigreturn`, `sys_rt_sigreturn`, `do_work_pending`, `get_signal_page`, and optional `do_rseq_syscall`. Internal helpers preserve/restore iWMMXt and VFP contexts, build `sigcontext`, choose signal stack, install return trampolines, and set handler registers.

Control flow: `do_work_pending` schedules, handles signals/uprobes/resume work, and may request syscall restart. `do_signal` converts restart errors, obtains a signal, adjusts syscall return behavior, and calls `handle_signal`. Frame setup writes user frames, signal masks, aux contexts, retcode, handler PC/LR/SP/CPSR, and realtime arguments. Return syscalls validate stack alignment/access, restore context and altstack, or SIGSEGV on bad frames.

State and persistence: mutates user stack frames, `pt_regs`, current blocked mask, restart block, VFP/iWMMXt hardware state, and `signal_return_offset`.

Dependencies and integration: signal core, uaccess, VFP/iWMMXt, rseq, uprobes, syscall restart ABI, process sigpage mapping, cache flushes, and static siginfo layout assertions.

Risks: signal frame ABI is user-visible and security-sensitive; invalid user frames must not restore privileged CPSR; trampoline cache flush and Thumb/ARM/FDPIC selection must be correct. Test signals include LTP signal tests, altstack, VFP/iWMMXt signal state, syscall restart, Thumb handlers, FDPIC, and malformed sigreturn fuzzing.
