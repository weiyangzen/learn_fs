<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/signal.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/signal.h

Purpose: provides x86 signal ABI glue, signal stack definitions, and architecture overrides layered on top of UAPI/generic signal headers. Important content includes signal type aliases, `__ARCH_HAS_SA_RESTORER`, and inclusion boundaries for kernel versus userspace.

Control flow: generic signal code uses these definitions to interpret user sigaction structures and restorer behavior on x86. State lives in task signal handlers and user signal frames. Dependencies include UAPI signal numbers, generic signal implementation, and x86 restorer ABI.

Risks: signal ABI is stable userspace contract; changing restorer or stack definitions can break libc and old binaries. Test signals include POSIX signal tests, sigaction restorer behavior, compat signal ABI, and libc signal trampoline compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/signal.h -->
