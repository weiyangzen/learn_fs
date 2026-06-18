# sources/distributed-fs/ceph-client/include/uapi/asm-generic/msgbuf.h

Purpose: Defines generic SysV message queue status structure layout.

Important APIs/types/functions: Exports `struct msqid64_ds` containing `ipc64_perm`, send/receive/change timestamps with 32-bit high halves on 32-bit user space, queue byte/message counts, byte limit, last sender/receiver pids, and unused fields.

Control flow: `__BITS_PER_LONG` selects direct long timestamp fields for 64-bit or split low/high fields for 32-bit.

State/persistence: No runtime state; struct is the user-kernel ABI for message queue status.

Dependencies/integration: Includes `asm/bitsperlong.h` and `asm/ipcbuf.h`; used by SysV IPC syscalls and libc.

Risks: Timestamp split layout and endian notes are ABI-sensitive. Padding changes break old user space.

Test signals: SysV message queue tests and struct layout checks on 32-bit and 64-bit ABIs.
