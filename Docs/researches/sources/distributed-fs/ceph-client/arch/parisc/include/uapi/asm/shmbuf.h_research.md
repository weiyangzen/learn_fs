<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/shmbuf.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/shmbuf.h

Source read size: 53 lines, 1481 bytes.

Purpose: defines PA-RISC SysV shared-memory metadata layouts. Important types: `struct shmid64_ds` and `struct shminfo64`, including permissions, split/native time fields, segment size, creator/last PID, attach count, limits, and padding. Control flow: shmctl IPC_STAT/IPC_INFO/SHM_INFO copies these layouts. State and persistence: describes persistent shared memory segment state and system limits. Dependencies and integration points: `bitsperlong.h`, `ipcbuf.h`, `posix_types.h`, SysV shm core, libc. Risks: 32-bit split time fields and `__kernel_size_t` sizing affect ABI. Test signals: shmget/shmat/shmdt/shmctl tests, 32-bit compat layout checks, and IPC namespace tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/shmbuf.h -->
