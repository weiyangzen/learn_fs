# sources/distributed-fs/ceph-client/arch/riscv/kernel/compat_signal.c

Purpose: Implements 32-bit compat signal frame setup and return for 64-bit RISC-V kernels running compat tasks.

Important APIs/types/functions: Defines `compat_sigcontext`, `compat_ucontext`, `compat_rt_sigframe`, and implements compat register save/restore, floating-point state movement, `compat_setup_rt_frame()`, and `compat_sys_rt_sigreturn()`.

Control flow: Signal delivery builds a compat rt frame on the user signal stack, copies siginfo/ucontext, saves integer and FP state, installs the handler PC, stack pointer, return address, and VDSO `rt_sigreturn` trampoline. `compat_sys_rt_sigreturn()` validates and copies the frame back, restores signal mask, register state, FP state, and returns through the normal syscall restart path.

State and persistence: State exists in the user-space signal frame and transient kernel `pt_regs`. Signal masks and alternate stack metadata persist in task signal state according to generic signal rules.

Dependencies and integration points: Depends on compat ABI structs, `asm/signal32.h`, RISC-V `pt_regs`, VDSO trampoline offsets, user access helpers, and generic Linux signal delivery.

Risks and test signals: ABI layout is user visible. Incorrect padding, stack alignment, FP restore, or trampoline address selection breaks 32-bit processes. Test with compat signal delivery, nested signals, alternate stacks, FP-heavy handlers, `sigreturn` fuzzing, and 32-bit userspace on RV64.
