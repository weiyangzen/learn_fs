# sources/distributed-fs/ceph-client/arch/sh/kernel/vsyscall/vsyscall-sigreturn.S

Purpose: provides vDSO signal-return trampolines for SH user processes.

Important symbols and sections: `__kernel_sigreturn`, `__kernel_rt_sigreturn`, `.eh_frame`, CIE/FDE records, and syscall numbers `__NR_sigreturn` and `__NR_rt_sigreturn`.

Control flow: each trampoline loads the appropriate signal-return syscall number into `r3` and executes `trapa #0x10`, returning control to the kernel signal frame restore path. Embedded unwind records describe the code ranges for user-space unwinding.

State and persistence: no mutable state; code and unwind metadata are embedded in the vDSO page mapped into each process.

Dependencies and integration: included by `vsyscall-trapa.S`, linked by `vsyscall.lds.S`, used by signal setup code and libc unwinding/debugging.

Risks: incorrect syscall number, trap immediate, or unwind encoding breaks signal return or backtraces through signal frames.

Test signals: user-space signal delivery/return tests, `rt_sigreturn` behavior, and debugger unwinding across a signal handler.
