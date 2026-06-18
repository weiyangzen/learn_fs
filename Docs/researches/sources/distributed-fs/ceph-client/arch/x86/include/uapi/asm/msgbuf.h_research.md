<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/msgbuf.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/msgbuf.h

Purpose: Selects the generic SysV message queue buffer ABI except for x32, where it defines the x86_64-compatible `msqid64_ds` layout using x32-sized kernel types.

Important APIs/types/functions: `struct msqid64_ds` for x32 and inclusion of `asm-generic/msgbuf.h` otherwise.

Control flow: SysV IPC syscalls copy this structure between kernel and userspace for message queue metadata.

State and persistence behavior: Message queue metadata persists in kernel IPC objects; this header defines the userspace serialization layout.

Dependencies and integration points: Depends on `asm/ipcbuf.h` and generic msgbuf. Integrates with SysV IPC, x32 ABI compatibility, libc, and checkpoint/restore tools.

Risks and test signals: Risks include x32 layout mismatch with x86_64 expectations and time/long width confusion. Test SysV message queue stat/control calls on i386, x86_64, and x32 builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/msgbuf.h -->
