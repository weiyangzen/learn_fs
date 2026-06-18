# sources/distributed-fs/ceph-client/include/uapi/linux/unistd.h

Purpose: Provides the generic include wrapper for architecture-specific syscall numbers.

Important APIs/types/functions: Includes `asm/unistd.h`, which defines `__NR_*` syscall numbers and related architecture declarations.

Control flow: No runtime flow; userspace compilation resolves syscall constants through the architecture header.

State and persistence behavior: No state.

Dependencies and integration points: Integrates with libc, syscall wrappers, seccomp filters, tracers, and architecture-specific UAPI.

Risks: Architecture-specific syscall numbering must be used; generic code must not assume identical `__NR_*` values across architectures.

Test signals: Compile syscall-using userspace for multiple target architectures and verify expected `__NR_*` presence for seccomp/tracing tests.
