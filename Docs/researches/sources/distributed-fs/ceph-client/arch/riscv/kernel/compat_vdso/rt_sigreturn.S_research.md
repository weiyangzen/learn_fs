# sources/distributed-fs/ceph-client/arch/riscv/kernel/compat_vdso/rt_sigreturn.S

Purpose: Provides the compat VDSO `rt_sigreturn` trampoline by compiling the common RISC-V VDSO signal-return source for the 32-bit ABI.

Important APIs/types/functions: Defines `VDSO_32BIT` and includes `../vdso/rt_sigreturn.S`.

Control flow: Signal setup points the user return address at this VDSO entry. When user handlers return, the entry issues the compat `rt_sigreturn` syscall, which is handled by compat signal restoration code.

State and persistence: No private state; it is executable code mapped in compat tasks.

Dependencies and integration points: Integrates with `compat_signal.c`, compat syscall numbers, and VDSO mapping.

Risks and test signals: Wrong syscall number or ABI mode prevents all compat signal handlers from returning correctly. Test with signal delivery, nested signals, alternate signal stacks, and seccomp/audit visibility of `rt_sigreturn`.
