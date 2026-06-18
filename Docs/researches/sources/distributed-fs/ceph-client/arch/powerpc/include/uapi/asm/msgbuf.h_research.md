<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/msgbuf.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/msgbuf.h

Purpose: Defines PowerPC SysV message queue status layout.

Important APIs/types/functions: `struct msqid64_ds` with `ipc64_perm`, timestamp fields split on 32-bit, byte/message limits, last sender/receiver PIDs, and padding.

Control flow: `msgctl` copies this layout to/from userspace depending on 32-bit or 64-bit ABI.

State and persistence: Represents persistent message queue metadata state.

Dependencies and integration points: Depends on `ipcbuf.h` and kernel pid/time UAPI types.

Risks: Timestamp split/high fields and padding are ABI-sensitive for compat tasks.

Test signals: SysV message queue tests on ppc32/ppc64, Y2038-oriented compat layout tests, and libc structure checks.

Source read size: 36 lines, 1159 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/msgbuf.h -->
