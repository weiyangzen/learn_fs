<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/ipcbuf.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/ipcbuf.h

Purpose: defines the Xtensa UAPI `struct ipc64_perm` used in System V IPC objects. Fields include key, uid/gid/cuid/cgid, mode, sequence, and two padding words.

Control flow is none; generic IPC syscalls copy this structure across the user/kernel boundary. Persistent state is IPC permission metadata in kernel IPC objects and userspace ABI buffers. Dependencies include `linux/posix_types.h`. Integration points are message queues, semaphores, shared memory, libc IPC APIs, and compat ABI layout. Risks are padding/field-size ABI regressions and mismatch with IPC object structures. Test signals include SysV IPC tests, structure size/offset checks, big/little endian builds, and headers_install.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/ipcbuf.h -->
