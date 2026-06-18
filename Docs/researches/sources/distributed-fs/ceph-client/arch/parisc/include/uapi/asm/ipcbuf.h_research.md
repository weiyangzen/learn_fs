<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/ipcbuf.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/ipcbuf.h

Source read size: 33 lines, 837 bytes.

Purpose: defines PA-RISC `ipc64_perm` layout for SysV IPC permissions. Important type: `struct ipc64_perm` with key, uid/gid, creator uid/gid, mode, sequence, padding, and unused expansion fields. Control flow: kernel SysV IPC syscalls copy this layout to/from userspace. State and persistence: describes persistent IPC object metadata for message queues, semaphores, and shared memory. Dependencies and integration points: included by `msgbuf.h`, `sembuf.h`, and `shmbuf.h`, with `bitsperlong` affecting padding. Risks: layout must remain stable across 32/64-bit userspace; `seq` is intentionally `unsigned short`/padding-sensitive. Test signals: SysV IPC creation/stat/control tests on 32-bit and 64-bit PA-RISC, structure-size checks, and libc IPC ABI tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/ipcbuf.h -->
