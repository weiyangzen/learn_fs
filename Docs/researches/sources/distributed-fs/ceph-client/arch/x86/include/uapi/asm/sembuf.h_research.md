<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/sembuf.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/sembuf.h

Purpose: Defines the x86 SysV semaphore `semid64_ds` userspace layout with ABI-specific time and padding fields.

Important APIs/types/functions: `struct semid64_ds`.

Control flow: SysV semaphore control syscalls copy this structure between kernel and userspace for semaphore set metadata.

State and persistence behavior: Semaphore metadata persists in kernel IPC objects; this header defines serialization, including historical padding differences between x86_32, x86_64, and x32.

Dependencies and integration points: Depends on `asm/ipcbuf.h`. Integrates with SysV IPC, libc, compat syscalls, and checkpoint/restore tools.

Risks and test signals: Risks include padding/layout mismatch and time field width confusion. Test `semctl(IPC_STAT/IPC_SET)` on i386, x86_64, and x32, plus ABI structure size checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/sembuf.h -->
