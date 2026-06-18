<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/Kbuild -->
# sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/Kbuild

Purpose: controls exported generated/generic UAPI headers for SH.

Important APIs/types/functions: `generated-y += unistd_32.h` and `generic-y += ucontext.h`.

Control flow: Kbuild exports a generated syscall header and reuses generic ucontext during headers install.

State and persistence: no runtime state; this affects installed kernel headers.

Dependencies/integration: integrates arch SH UAPI with scripts/headers_install and syscall generation.

Risks: missing generated header breaks libc builds; wrong generic header changes user ABI.

Test signals: run `make headers_install` for SH and compile a minimal userspace program.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/Kbuild -->
