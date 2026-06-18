## sources/distributed-fs/ceph-client/arch/s390/include/asm/unistd.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/asm/unistd.h` is a s390 syscall-number
integration in the s390 ceph-client Linux source snapshot. It has 35 lines and 910 bytes; exported
UAPI contract: no.

### Important APIs, Types, And Functions
UAPI syscall inclusion plus architecture feature wants for legacy and compatibility syscalls
Important macros/constants: `_ASM_S390_UNISTD_H_`, `NR_syscalls`, `__ARCH_WANT_NEW_STAT`, `__ARCH_WANT_OLD_READDIR`, `__ARCH_WANT_SYS_ALARM`, `__ARCH_WANT_SYS_GETHOSTNAME`, `__ARCH_WANT_SYS_PAUSE`, `__ARCH_WANT_SYS_SIGNAL`, `__ARCH_WANT_SYS_UTIME`, `__ARCH_WANT_SYS_SOCKETCALL`, `__ARCH_WANT_SYS_IPC`, `__ARCH_WANT_SYS_FADVISE64`, `__ARCH_WANT_SYS_GETPGRP`, `__ARCH_WANT_SYS_NICE`, `__ARCH_WANT_SYS_OLD_GETRLIMIT`, `__ARCH_WANT_SYS_OLD_MMAP`, `__ARCH_WANT_SYS_OLDUMOUNT`, `__ARCH_WANT_SYS_SIGPENDING`, `__ARCH_WANT_SYS_SIGPROCMASK`, `__ARCH_WANT_SYS_FORK`; plus 2 more.
Important types/layouts: none detected.
Important declarations or inline helpers: none detected.

### Control Flow
Control flow is inlined into callers. The header selects the appropriate architecture-specific
helper, executes any embedded instruction sequence or simple predicate, and returns normalized C
values to generic kernel code.

### State And Persistence
Most state is external to the header: CPU registers, lowcore fields, page tables, control blocks, or
caller-owned structures. Inline helpers may update hardware-visible state or caller buffers, but the
header does not allocate durable storage.

### Dependencies
generated syscall tables, seccomp, audit, and syscall wrappers. Direct include dependencies detected
here: `uapi/asm/unistd.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/asm` source-
tree area and feeds the s390 architecture boundary for generated syscall tables, seccomp, audit, and
syscall wrappers. For UAPI files, the integration point also includes headers_install and userspace
programs compiled against the exported layout.

### Risks
wrong NR_syscalls or __ARCH_WANT flags break userspace ABI compatibility

### Test Signals
syscall table generation, strace/seccomp tests, and compat userspace smoke tests
