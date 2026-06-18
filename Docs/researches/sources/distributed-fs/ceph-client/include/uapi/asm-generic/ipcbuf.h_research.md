# sources/distributed-fs/ceph-client/include/uapi/asm-generic/ipcbuf.h

Purpose: Defines the generic SysV IPC permission structure shared by message queues, semaphores, and shared memory UAPI.

Important APIs/types/functions: Exports `struct ipc64_perm` with key, uid/gid/cuid/cgid, mode, padding, sequence, and unused extension fields.

Control flow: Header-only struct definition; padding handles mode_t width and future expansion.

State/persistence: No runtime state; struct layout is copied across user/kernel syscall boundaries.

Dependencies/integration: Includes `linux/posix_types.h`; embedded by `msgbuf.h`, `sembuf.h`, and `shmbuf.h`.

Risks: Padding and field widths are ABI-sensitive across 32/64-bit userspace and endian variants.

Test signals: SysV IPC userspace tests and ABI layout comparisons for `ipc64_perm`.
