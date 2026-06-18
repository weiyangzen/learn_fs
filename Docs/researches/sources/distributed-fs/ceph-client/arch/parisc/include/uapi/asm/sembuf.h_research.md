<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/sembuf.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/sembuf.h

Source read size: 33 lines, 908 bytes.

Purpose: defines PA-RISC `semid64_ds` for SysV semaphores. Important type: `struct semid64_ds` with `ipc64_perm`, 64-bit or split time fields, semaphore count, and padding. Control flow: semctl IPC_STAT/IPC_SET copies this structure. State and persistence: describes persistent semaphore array metadata. Dependencies and integration points: `bitsperlong.h`, `ipcbuf.h`, SysV semaphore core, libc. Risks: time field order and padding differ by word size and must remain ABI-stable. Test signals: semget/semop/semctl IPC_STAT tests, 32-bit compat layout checks, and y2038 coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/sembuf.h -->
