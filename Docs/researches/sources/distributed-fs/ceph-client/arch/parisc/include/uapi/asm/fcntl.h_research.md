<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/fcntl.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/fcntl.h

Source read size: 39 lines, 1024 bytes.

Purpose: defines PA-RISC file open and fcntl command constants before including generic fcntl definitions. Important APIs: architecture-specific `O_*` flag values, `F_GETLK64`, `F_SETLK64`, `F_SETLKW64`, socket-owner fcntl commands, and lock-type constants. Control flow: userspace passes these values to open/fcntl syscalls; kernel VFS decodes them. State and persistence: file descriptor flags and locks persist in kernel objects, while constants are ABI. Dependencies and integration points: VFS, libc, POSIX locking, socket ownership, and compat syscall handling. Risks: PA-RISC flag numbers are non-generic; changing or mixing them breaks binaries and wrong-open flag decoding. Test signals: open flag tests, large-file locking tests, socket `F_SETOWN`/`F_SETSIG`, and headers_install ABI checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/fcntl.h -->
