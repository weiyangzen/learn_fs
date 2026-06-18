<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/signal.c -->
# sources/distributed-fs/ceph-client/arch/openrisc/kernel/signal.c

## Purpose
Implements OpenRISC signal-frame creation, `rt_sigreturn`, FPU signal state, syscall restart decisions, and userspace return work processing.

## Important APIs, Types, And Functions
Defines `struct rt_sigframe`, `_sys_rt_sigreturn()`, `restore_sigcontext()`, `setup_sigcontext()`, `get_sigframe()`, `setup_rt_frame()`, `handle_signal()`, `do_signal()`, and `do_work_pending()`.

## Control Flow
Signal delivery chooses user or alt stack, writes siginfo/ucontext/mask and a small `rt_sigreturn` trampoline, then redirects PC and arguments to the handler. `rt_sigreturn` validates frame alignment/access, restores signal mask, registers, FPU state, and alt stack. `do_signal()` handles syscall restart values before and after `get_signal()`.

## State And Persistence
Persists saved registers/FPU/mask on the user stack. Mutates live `pt_regs`, blocked signal mask, restart block, and optional FPU state.

## Dependencies And Integration Points
Depends on UAPI sigcontext/ucontext, usercopy, FPU helpers, syscall register ABI, `entry.S` return path, and `resume_user_mode_work()`.

## Risks
Signal-frame ABI is fragile. Kernel must clear `SPR_SR_SM` on restore to prevent user supervisor mode. Trampoline instruction encoding and syscall number must match the ABI.

## Test Signals
Signal delivery/return, SA_SIGINFO, altstack, syscall restart variants, ptrace interaction during signals, and FPU `fpcsr` preservation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/signal.c -->
