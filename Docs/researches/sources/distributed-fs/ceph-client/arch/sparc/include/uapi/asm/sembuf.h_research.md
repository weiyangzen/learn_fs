<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/sembuf.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/sembuf.h

Purpose: Defines SPARC `semid64_ds` SysV semaphore ABI layout.

Important APIs and control flow: embeds `ipc64_perm`, stores operation/change times as native longs or high/low pairs, semaphore count, and reserved fields. The layout is used by semctl IPC_STAT/IPC_SET paths.

State, dependencies, and risks: state is semaphore-array metadata. Dependencies include `asm/ipcbuf.h` and SysV semaphore code. Risks are time-field and padding compatibility, especially across 32-bit and 64-bit processes. Test signals are semctl structure round trips and ABI layout checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/sembuf.h -->
