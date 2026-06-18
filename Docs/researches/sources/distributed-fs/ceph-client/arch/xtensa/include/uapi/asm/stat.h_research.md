<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/stat.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/stat.h

Purpose: defines Xtensa UAPI `struct stat` and `struct stat64` layouts and sets `STAT_HAVE_NSEC`. Fields cover device/inode, mode/link count, uid/gid, rdev, size, block size/count, atime/mtime/ctime with nanoseconds, and padding.

Control flow is syscall copyout/copyin through stat-family syscalls. Persistent state represented is filesystem inode metadata in user ABI buffers. Dependencies include kernel syscall wants in `asm/unistd.h` and generic VFS stat conversion. Integration points are libc `stat`, old/new/stat64 syscalls, filesystems, tar/core utilities, and strace. Risks are structure layout ABI stability, 32-bit time range constraints, and inconsistency between `stat` and `stat64`. Test signals include stat syscall tests, large file tests, nanosecond timestamp checks, structure offset validation, and headers_install.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/stat.h -->
