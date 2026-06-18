<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/stat.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/stat.h

Purpose: Defines x86 `stat`, `stat64`, and old stat layouts, including i386-specific padding and x86_64 generic-width fields.

Important APIs/types/functions: `STAT_HAVE_NSEC`, `struct stat` for i386 and non-i386, `INIT_STRUCT_STAT_PADDING()`, i386 `struct stat64`, `INIT_STRUCT_STAT64_PADDING()`, `STAT64_HAS_BROKEN_ST_INO`, and `struct __old_kernel_stat`.

Control flow: Kernel stat syscalls copy these structures to userspace; padding macros let kernel code initialize only the ABI padding that matters.

State and persistence behavior: No state. Structures serialize filesystem inode metadata to userspace, including nanosecond timestamps.

Dependencies and integration points: Depends on POSIX types. Integrates with VFS stat family syscalls, libc, 32-bit compatibility, old binaries, and filesystem metadata reporting.

Risks and test signals: Risks include padding leaks, broken i386 inode layout compatibility, time/size truncation, and x32/x86_64 type mismatch. Test stat/stat64/lstat/fstat on i386 and x86_64, ABI struct sizes, padding zeroing, large inode numbers, and nanosecond timestamp reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/stat.h -->
