<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/start_kernel.h -->
# sources/distributed-fs/ceph-client/include/linux/start_kernel.h

Purpose: Provides the canonical prototype for the kernel entry function `start_kernel()`.

Important APIs/types/functions: `extern asmlinkage void __init __noreturn start_kernel(void);`.

Control flow: No implementation here. Architecture boot code eventually calls `start_kernel()`, which never returns.

State and persistence behavior: No state in the header; annotations place implementation in init context and mark non-returning behavior.

Dependencies: `linkage.h` and `init.h` for calling convention and section/lifetime annotations.

Integration points: Architecture boot assembly/C handoff and early kernel initialization.

Risks: Signature or annotation mismatch would break boot entry linkage or compiler assumptions.

Test signals: Architecture boot builds, linker symbol checks, and early boot smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/start_kernel.h -->
