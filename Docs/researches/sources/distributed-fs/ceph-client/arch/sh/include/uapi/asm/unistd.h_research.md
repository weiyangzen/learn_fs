<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/unistd.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/unistd.h

Purpose: routes SH syscall number declarations to the generated 32-bit table.

Important APIs/types/functions: includes `unistd_32.h` through generated UAPI flow.

Control flow: syscall numbers are consumed by libc and kernel syscall dispatch code.

State and persistence: no runtime state in this file.

Dependencies/integration: depends on Kbuild generating `unistd_32.h`.

Risks: missing generation breaks all userspace syscall builds.

Test signals: run headers_install and compile syscall-number users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/unistd.h -->
