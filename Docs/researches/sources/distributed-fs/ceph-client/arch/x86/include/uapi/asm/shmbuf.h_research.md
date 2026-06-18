<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/shmbuf.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/shmbuf.h

Purpose: Selects generic SysV shared-memory buffer definitions except for x32, where it defines x86_64-compatible `shmid64_ds` and `shminfo64` layouts.

Important APIs/types/functions: `struct shmid64_ds` and `struct shminfo64` for x32, otherwise inclusion of `asm-generic/shmbuf.h`.

Control flow: SysV shared-memory syscalls copy these structures between kernel and userspace for segment metadata and system limits.

State and persistence behavior: Shared-memory metadata persists in kernel IPC objects; this header preserves userspace serialization for x32 and other x86 ABIs.

Dependencies and integration points: Depends on `asm/ipcbuf.h`, `asm/posix_types.h`, and generic shmbuf. Integrates with SysV IPC, x32 compatibility, libc, and checkpoint/restore tools.

Risks and test signals: Risks include x32 layout mismatch, time/size width errors, and padding incompatibility. Test `shmctl(IPC_STAT/IPC_INFO)` on i386, x86_64, and x32 plus ABI size checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/shmbuf.h -->
