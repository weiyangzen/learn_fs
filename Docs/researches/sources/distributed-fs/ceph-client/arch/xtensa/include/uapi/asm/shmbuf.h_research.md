<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/shmbuf.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/shmbuf.h

Purpose: defines Xtensa UAPI shared-memory metadata structures `struct shmid64_ds` and `struct shminfo64`. `shmid64_ds` contains permissions, segment size, attach/detach/change timestamps with high words, creator/last PIDs, attach count, and padding; `shminfo64` contains shm limits and padding.

Control flow is generic SysV shm syscall copying. Persistent state represented is shared memory segment metadata and system limits. Dependencies include `asm/ipcbuf.h` and `asm/posix_types.h`. Integration points are `shmctl`, `shmat`, libc IPC APIs, cache-aligned shared memory mapping, and CRIU-like tools. Risks include historically wrong-side padding for big-endian Xtensa, size_t width assumptions, and timestamp ABI stability. Test signals include shmget/shmat/shmctl tests, endian structure offset checks, headers_install, and shared-memory alignment/cache stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/shmbuf.h -->
