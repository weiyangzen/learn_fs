<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/ipcbuf.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/ipcbuf.h

Purpose: Defines SPARC `ipc64_perm` layout for SysV IPC user ABI.

Important APIs and control flow: the structure stores key, owner/creator IDs, mode, sequence, and reserved padding. A conditional pad keeps 32-bit and 64-bit layouts aligned with kernel/user exchange expectations.

State, dependencies, and risks: state is IPC object metadata passed through msgctl/semctl/shmctl. Dependencies include Linux POSIX type definitions and the IPC subsystem. Risks are padding changes breaking old binaries and mismatched sequence width. Test signals are IPC permission round trips on 32-bit and 64-bit SPARC and structure layout checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/ipcbuf.h -->
