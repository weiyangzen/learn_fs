<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/sembuf.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/sembuf.h

Purpose: Defines PowerPC SysV semaphore status layout.

Important APIs/types/functions: `struct semid64_ds` with permission, timestamp fields split for 32-bit, semaphore count, and padding.

Control flow: `semctl` copies this structure for IPC status and updates.

State and persistence: Represents persistent semaphore set metadata.

Dependencies and integration points: Depends on `ipcbuf.h` and SysV IPC kernel code.

Risks: Timestamp split fields and padding are ABI-sensitive.

Test signals: SysV semaphore tests on ppc32/ppc64, compat layout checks, and libc conformance.

Source read size: 39 lines, 1144 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/sembuf.h -->
