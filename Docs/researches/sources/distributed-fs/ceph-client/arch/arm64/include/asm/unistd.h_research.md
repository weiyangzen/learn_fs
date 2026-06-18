<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/unistd.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/unistd.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/unistd.h` connects arm64 syscall numbering to generated `unistd_64.h`, declares compatibility syscall feature wants, and defines the AArch32 private compatibility syscall range. It belongs to the arm64 Linux-kernel compatibility code imported under the Ceph client source tree, so Ceph depends on it indirectly through the kernel facilities that make networking, memory management, page cache, and filesystem execution work on arm64.

### Important APIs, Types, And Functions
macros: `__ARCH_WANT_COMPAT_STAT`, `__ARCH_WANT_COMPAT_STAT64`, `__ARCH_WANT_SYS_GETHOSTNAME`, `__ARCH_WANT_SYS_PAUSE`, `__ARCH_WANT_SYS_GETPGRP`, `__ARCH_WANT_SYS_NICE`, `__ARCH_WANT_SYS_SIGPENDING`, `__ARCH_WANT_SYS_SIGPROCMASK`, `__ARCH_WANT_COMPAT_SYS_SENDFILE`, `__ARCH_WANT_SYS_UTIME32`, `__ARCH_WANT_SYS_FORK`, `__ARCH_WANT_SYS_VFORK`, `__ARM_NR_COMPAT_BASE`, `__ARM_NR_compat_cacheflush`, `__ARM_NR_compat_set_tls`, `__ARM_NR_COMPAT_END`, `__ARCH_WANT_SYS_CLONE`, `__ARCH_WANT_NEW_STAT`, `NR_syscalls`. The file is 33 lines / 898 bytes. Direct includes are `asm/unistd_64.h`.

### Control Flow
There is no runtime control flow; syscall dispatch tables and generic syscall glue consume these macros at build time. The compat block is enabled only under `CONFIG_COMPAT`.

### State, Persistence, And Dependencies
The file contributes ABI constants only. Persistence is in the stable userspace/kernel syscall ABI, not in kernel storage. Integration dependencies include generic Linux arm64 architecture code, Kbuild/UAPI generation where applicable, and any included subsystem headers listed above.

### Integration Points
This file integrates with arm64 architecture boot, exception, syscall, virtualization, vDSO, ACPI, Xen, MM, or UAPI consumers according to its exported surface. In this Ceph client source snapshot, the integration is architectural rather than Ceph-protocol-specific: the distributed filesystem client relies on these contracts for safe user copies, syscall ABI stability, vDSO time, CPU feature handling, virtualization, ACPI boot, and compat execution on arm64 systems.

### Risks
ABI drift between generated syscall tables, compat syscall numbers, and userspace headers can break seccomp, tracing, libc, or 32-bit process compatibility.

### Test Signals
Run arm64 and compat syscall table generation checks, build with and without `CONFIG_COMPAT`, and exercise syscall selftests and strace/seccomp decoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/unistd.h -->
