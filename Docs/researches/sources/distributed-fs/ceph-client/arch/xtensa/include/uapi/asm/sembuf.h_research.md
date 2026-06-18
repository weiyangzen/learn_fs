<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/sembuf.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/sembuf.h

Purpose: defines Xtensa UAPI `struct semid64_ds` for System V semaphores, including permissions, endian-ordered split operation/change timestamps, semaphore count, and padding.

Control flow is generic SysV semaphore syscall copying. Persistent state represented is semaphore-set metadata in kernel IPC state and userspace buffers. Dependencies include `asm/byteorder.h` and `asm/ipcbuf.h`. Integration points are libc `semctl`, IPC tools, checkpoint/restore, and strace. Risks are endian timestamp ordering, padding ABI stability, and 32-bit time handling. Test signals include semget/semop/semctl selftests, structure offset validation, big/little endian builds, and headers_install.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/sembuf.h -->
