<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/uapi/asm/unistd.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/uapi/asm/unistd.h

Purpose: Defines RISC-V UAPI syscall number inclusions and architecture-specific syscall availability.

Important APIs/types/functions: Sets `__ARCH_WANT_NEW_STAT`, `__ARCH_WANT_SET_GET_RLIMIT`, includes generic unistd, and defines RISC-V arch syscall numbers such as `riscv_hwprobe` where applicable.

Control flow: Userspace and kernel generated tables compile against these numbers.

State and persistence: Stable syscall ABI numbering.

Dependencies and integration points: Used by libc, seccomp, syscall tables, strace, and VDSO/syscall wrappers.

Risks: Changing numbers or feature wants breaks userspace ABI.

Test signals: headers_install, libc syscall tests, strace/seccomp, and syscall table generation.

Source read size: 23 lines, 852 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/uapi/asm/unistd.h -->
