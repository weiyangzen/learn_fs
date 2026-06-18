<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/sockios.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/sockios.h

Purpose: defines SH socket ioctl command numbers.

Important APIs/types/functions: `FIOGETOWN`, `FIOSETOWN`, `SIOCATMARK`, `SIOCSPGRP`, `SIOCGPGRP`, old timestamp ioctls.

Control flow: socket ioctl syscall dispatches these values to networking state handlers.

State and persistence: state is socket ownership, process group, mark, and timestamps outside this header.

Dependencies/integration: integrates libc networking headers and kernel socket ioctl handling.

Risks: number drift breaks network tools compiled for SH.

Test signals: run socket ioctl ABI smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/sockios.h -->
