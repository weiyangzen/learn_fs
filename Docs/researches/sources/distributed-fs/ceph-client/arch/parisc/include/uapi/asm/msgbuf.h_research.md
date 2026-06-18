<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/msgbuf.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/msgbuf.h

Source read size: 40 lines, 1246 bytes.

Purpose: defines PA-RISC `msqid64_ds` layout for SysV message queues. Important type: `struct msqid64_ds` containing `ipc64_perm`, split or native time fields, queue byte/message counters, last sender/receiver PIDs, and padding. Control flow: msgctl IPC_STAT/IPC_SET copies this structure between kernel and userspace. State and persistence: describes persistent message queue state. Dependencies and integration points: depends on `bitsperlong.h` and `ipcbuf.h`; used by SysV IPC and libc. Risks: split high/low time fields on 32-bit builds and padding must remain ABI-compatible. Test signals: msgget/msgsnd/msgrcv/msgctl tests, y2038/time-size checks, and 32-bit compat structure-size validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/msgbuf.h -->
