<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/ipcbuf.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/ipcbuf.h

Purpose: Defines PowerPC `ipc64_perm` layout for SysV IPC user ABI.

Important APIs/types/functions: `struct ipc64_perm` with key, uid/gid/cuid/cgid, mode, sequence, padding, and unused 64-bit slots.

Control flow: SysV IPC syscalls copy this structure between kernel and userspace for permission metadata.

State and persistence: Represents persistent IPC object permission state, with padding reserved for ABI growth/alignment.

Dependencies and integration points: Depends on Linux UAPI types and is embedded by msg/sem/shm buffer headers.

Risks: Field order, sizes, and padding are ABI-sensitive, especially across 32-bit and 64-bit tasks.

Test signals: SysV IPC permission tests, compat syscall tests, and structure layout checks against libc.

Source read size: 35 lines, 1057 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/ipcbuf.h -->
