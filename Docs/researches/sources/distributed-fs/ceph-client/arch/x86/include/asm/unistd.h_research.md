# sources/distributed-fs/ceph-client/arch/x86/include/asm/unistd.h

Purpose: selects x86 syscall number tables and architecture compatibility `__ARCH_WANT_*` feature flags.

Important APIs/types/functions: includes UAPI syscall numbers plus `unistd_32.h`, `unistd_64.h`, `unistd_64_x32.h`, `unistd_32_ia32.h`; defines `NR_syscalls`, `IA32_NR_syscalls`, and `X32_NR_syscalls`.

Control flow: 32-bit builds include native i386 syscalls and legacy wants. 64-bit builds include native, x32, and ia32 compat tables and define compat syscall feature requests.

State/persistence: no runtime state; this is a compile-time ABI selection point.

Dependencies/integration: used by syscall table generation, compat syscall handlers, seccomp/audit ABI metadata, and architecture build logic.

Risks/test signals: wrong table or count breaks syscall dispatch and compat ABI. Test native x86_64, i386, ia32 compat, x32 if enabled, seccomp syscall numbering, strace smoke tests, and syscall ABI selftests.
