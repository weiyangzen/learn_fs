<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/unistd.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/unistd.h

Purpose: Defines kernel-side RISC-V syscall numbering policy and generic syscall feature selections.

Important APIs/types/functions: Sets `__ARCH_WANT_*` feature macros, includes UAPI `asm/unistd.h`, and exposes `NR_syscalls` for kernel code.

Control flow: No runtime flow; generated syscall tables and wrappers use these constants.

State and persistence: No mutable state; syscall numbers are ABI state.

Dependencies and integration points: Used by syscall table generation, seccomp, audit, and compat logic.

Risks: Changing feature macros or counts changes syscall ABI/dispatch.

Test signals: Syscall table generation, libc smoke tests, seccomp, strace, and compat builds.

Source read size: 29 lines, 719 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/unistd.h -->
