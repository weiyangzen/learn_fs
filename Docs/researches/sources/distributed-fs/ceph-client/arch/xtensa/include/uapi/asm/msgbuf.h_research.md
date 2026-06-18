<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/msgbuf.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/msgbuf.h

Purpose: defines Xtensa UAPI `struct msqid64_ds` for System V message queues, including permission data, split high/low timestamp fields ordered by endianness, byte/message counts, queue size limit, last sender/receiver PIDs, and padding.

Control flow is none; generic IPC message queue syscalls copy this layout to/from userspace. Persistent state represented is kernel message-queue metadata. Dependencies include `asm/ipcbuf.h` and endian macros. Integration points are libc `msgctl`, checkpoint/restore tools, strace, and SysV IPC tests. Risks include endian-specific timestamp layout regressions, 32-bit time extension handling, and padding ABI stability. Test signals include msgget/msgsnd/msgrcv/msgctl tests, structure offset checks for both endian modes, and headers_install.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/msgbuf.h -->
