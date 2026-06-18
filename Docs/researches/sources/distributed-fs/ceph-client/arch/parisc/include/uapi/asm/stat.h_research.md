<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/stat.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/stat.h

Source read size: 68 lines, 1803 bytes.

Purpose: defines PA-RISC `struct stat` and `struct stat64` layouts. Important types: legacy `struct stat` with 32-bit device/inode/size/time fields plus HP-UX-derived spare fields, `STAT_HAVE_NSEC`, and `struct stat64` with 64-bit dev/rdev/size/blocks/inode and nanosecond fields. Control flow: stat-family syscalls copy these layouts to userspace. State and persistence: describes filesystem metadata snapshots. Dependencies and integration points: VFS stat code, libc, compat stat syscalls, and `asm/unistd.h` feature selectors. Risks: layout is unusual and explicitly intended to avoid wrappers for 32-bit userspace; changing fields breaks libc and old binaries. Test signals: stat/lstat/fstat/statx comparisons, large inode and large file tests, nanosecond timestamp tests, and 32/64-bit ABI size checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/stat.h -->
