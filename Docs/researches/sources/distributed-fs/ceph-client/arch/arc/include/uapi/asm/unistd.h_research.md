# sources/distributed-fs/ceph-client/arch/arc/include/uapi/asm/unistd.h

Userspace syscall-number include for ARC. It includes generated asm/unistd_32.h and exports no extra logic. Control flow is libc and userspace builds including syscall numbers, while kernel asm/unistd.h wraps it for NR_syscalls and __ARCH_WANT_* flags. State is generated syscall ABI. Dependencies are syscall table generation. Risks are stale generated unistd_32.h or missing headers_install coverage. Test signals are headers_install, libc syscall wrappers, and strace numbering.
