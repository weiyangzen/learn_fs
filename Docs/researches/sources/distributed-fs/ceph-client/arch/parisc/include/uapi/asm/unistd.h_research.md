<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/unistd.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/unistd.h

Source read size: 13 lines, 292 bytes.

Purpose: provides the exported PA-RISC syscall-number header by including generated 32-bit or 64-bit syscall lists according to `__BITS_PER_LONG`. Important APIs: generated `unistd_32.h`/`unistd_64.h` contents and `__NR_syscalls`. Control flow: preprocessor selects the generated table for userspace compilation. State and persistence: syscall numbers are permanent ABI. Dependencies and integration points: Kbuild generated headers, libc syscall wrappers, seccomp, audit, strace, and kernel syscall table. Risks: wrong word-size selection or generated-header drift breaks every syscall wrapper. Test signals: headers_install, syscall table consistency scripts, seccomp filter tests, strace syscall number decoding, and 32/64-bit userspace smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/unistd.h -->
