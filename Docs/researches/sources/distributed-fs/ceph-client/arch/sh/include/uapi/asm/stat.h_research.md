<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/stat.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/stat.h

Purpose: defines SH old/new stat structures and flags.

Important APIs/types/functions: `struct __old_kernel_stat`, `struct stat`, `struct stat64`, `STAT64_HAS_BROKEN_ST_INO`, `STAT_HAVE_NSEC`.

Control flow: stat-family syscalls fill these layouts for userspace.

State and persistence: state is filesystem inode metadata serialized through fixed ABI fields.

Dependencies/integration: integrates VFS stat translation, libc, and compat old-stat users.

Risks: padding/order changes corrupt userspace file metadata interpretation.

Test signals: run stat/stat64 ABI size-offset checks and filesystem stat tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/stat.h -->
