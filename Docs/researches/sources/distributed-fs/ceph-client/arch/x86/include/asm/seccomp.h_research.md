<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/seccomp.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/seccomp.h

Purpose: defines x86 seccomp audit architecture constants and syscall argument mappings for native and compat ABIs. Important macros include `SECCOMP_ARCH_NATIVE`, `SECCOMP_ARCH_NATIVE_NR`, `SECCOMP_ARCH_COMPAT`, `SECCOMP_ARCH_COMPAT_NR`, and register-index mappings for syscall arguments.

Control flow: seccomp and BPF syscall filters use these constants to expose syscall numbers and arguments consistently across x86-64, i386, and x32/compat modes. State is per-task seccomp state owned by generic code.

Dependencies include syscall ABI, audit arch values, ptrace register layout, and compat configuration. Risks include wrong argument register mapping causing filters to allow or deny the wrong syscalls, especially in compat/x32 modes. Test signals include seccomp-bpf selftests on native and compat binaries, audit arch checks, and syscall argument filter tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/seccomp.h -->
