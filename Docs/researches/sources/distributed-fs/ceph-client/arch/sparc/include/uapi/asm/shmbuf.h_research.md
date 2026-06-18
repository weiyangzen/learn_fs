<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/shmbuf.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/shmbuf.h

Purpose: Defines SPARC SysV shared-memory ABI structures.

Important APIs and control flow: `shmid64_ds` carries permissions, attach/detach/change times, segment size, creator/last-operation pids, attach count, and reserved fields with 32-bit/64-bit time layout conditionals. `shminfo64` exposes system shared-memory limits and padding.

State, dependencies, and risks: state is shared-memory segment metadata and global limits. Dependencies include `asm/ipcbuf.h`, `asm/posix_types.h`, and SysV shm control code. Risks are structure padding and time-size compatibility. Test signals are shmctl IPC_STAT/IPC_INFO tests, 32-bit compat checks, and large segment size reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/shmbuf.h -->
