<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/stat.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/stat.h

Purpose: Defines SPARC `stat` and `stat64` user ABI layouts.

Important APIs and control flow: 64-bit SPARC has compact `struct stat` and wider `struct stat64` with nsec fields and reserved padding. 32-bit SPARC has legacy `struct stat` with `STAT_HAVE_NSEC` and a padded `struct stat64` carrying 64-bit dev/ino/rdev/size plus 32-bit timestamps and nsec fields.

State, dependencies, and risks: state is filesystem inode metadata copied to userspace. Dependencies include Linux type definitions and VFS stat translation. Risks are layout drift, y2038 behavior on 32-bit stat64, device/inode truncation, and libc mismatches. Test signals are stat/lstat/fstat/stat64 syscall tests, large inode/device tests, timestamp nsec checks, and 32-bit compat validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/stat.h -->
