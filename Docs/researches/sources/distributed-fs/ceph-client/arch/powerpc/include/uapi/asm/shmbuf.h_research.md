<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/shmbuf.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/shmbuf.h

Purpose: Defines PowerPC SysV shared-memory status and limits structures.

Important APIs/types/functions: `struct shmid64_ds` and `struct shminfo64` with 32-bit timestamp splits, segment size, PIDs, attach count, and padding.

Control flow: `shmctl` copies these layouts for shared-memory metadata and limit queries.

State and persistence: Represents persistent shared-memory segment metadata and system limits.

Dependencies and integration points: Depends on IPC and POSIX type headers and SysV SHM kernel code.

Risks: Field order, timestamp handling, and padding are ABI-sensitive.

Test signals: SysV shared-memory tests, compat layout checks, and libc structure comparisons.

Source read size: 60 lines, 1723 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/shmbuf.h -->
