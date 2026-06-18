<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/msgbuf.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/msgbuf.h

Purpose: Defines SPARC `msqid64_ds` SysV message-queue ABI layout.

Important APIs and control flow: embeds `ipc64_perm`, stores send/receive/change times with 64-bit-native longs or high/low 32-bit fields, queue byte/message counts, byte limit, last sender/receiver pids, and reserved fields.

State, dependencies, and risks: state is message-queue metadata returned to userspace. Dependencies include `asm/ipcbuf.h` and SysV IPC control paths. Risks are time-field layout compatibility, unsigned long size variation, and padding changes. Test signals are `msgctl(IPC_STAT)` on 32-bit/64-bit SPARC, y2038/time64 checks, and IPC namespace tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/msgbuf.h -->
