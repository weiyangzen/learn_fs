<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/unistd.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/unistd.h

Purpose: selects LoongArch syscall table metadata for kernel builds.
Important APIs and types: defines `__ARCH_WANT_*` feature macros and includes UAPI syscall numbers.
Control flow: syscall dispatch and table generation use these constants at build time; no runtime flow lives here.
State and persistence: syscall-number ABI is persistent user/kernel contract.
Dependencies and integration: integrates with `include/uapi/asm/unistd.h`, syscall table generation, audit/seccomp, and libc headers.
Risks and test signals: wrong selection breaks syscall availability. Signals include syscall ABI builds, `strace`, libc tests, and seccomp/audit coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/unistd.h -->
