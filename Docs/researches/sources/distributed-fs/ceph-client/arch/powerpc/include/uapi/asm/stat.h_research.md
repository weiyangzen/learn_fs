<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/stat.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/stat.h

Purpose: Defines PowerPC legacy and current stat structure layouts.

Important APIs/types/functions: `STAT_HAVE_NSEC`, 32-bit `struct __old_kernel_stat`, `struct stat`, and 32-bit `struct stat64` matching glibc 2.1 layout.

Control flow: stat-family syscalls copy file metadata into these ABI-specific layouts, with ppc64 and ppc32 field ordering differences.

State and persistence: Structures serialize VFS inode metadata and timestamps to userspace.

Dependencies and integration points: Depends on Linux UAPI types, VFS stat conversion, and libc.

Risks: Field sizes/order and nanosecond fields are ABI-sensitive. 32-bit `stat64` must match old glibc expectations.

Test signals: stat/lstat/fstat tests on ppc32/ppc64, large inode/device tests, timestamp nanosecond checks, and libc structure comparisons.

Source read size: 82 lines, 2362 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/stat.h -->
