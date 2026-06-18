<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/errno.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/errno.h

Source read size: 127 lines, 5745 bytes.

Purpose: defines PA-RISC userspace errno numbering, combining generic base errors with HP-UX-compatible and Linux-specific values. Important APIs: constants from `ENOMSG` through `EHWPOISON`, aliases such as `EDEADLOCK`, `EWOULDBLOCK`, `ECANCELED`, and filesystem aliases `EFSBADCRC`/`EFSCORRUPTED`. Control flow: none; syscall return decoding and libc use these numbers. State and persistence: permanent userspace ABI. Dependencies and integration points: libc, strace, audit, network/filesystem syscalls, and compatibility code. Risks: numeric changes are ABI-breaking and can make userspace mis-handle syscall failures; PA-RISC values differ from many other Linux architectures. Test signals: libc errno tables, strace decoding, syscall failure tests, and cross-arch ABI validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/errno.h -->
