<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/posix_types.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/posix_types.h

Purpose: delegates SH POSIX type definitions to the 32-bit header.

Important APIs/types/functions: includes `posix_types_32.h`.

Control flow: compile-time include routing only.

State and persistence: no runtime state.

Dependencies/integration: used by libc and kernel UAPI headers needing `__kernel_*` types.

Risks: wrong include breaks all userspace ABI type widths.

Test signals: headers_install and compile stat/ioctl/signal users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/posix_types.h -->
