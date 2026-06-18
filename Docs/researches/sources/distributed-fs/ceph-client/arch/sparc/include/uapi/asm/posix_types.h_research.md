<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/posix_types.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/posix_types.h

Purpose: Supplies SPARC-specific kernel POSIX typedefs before generic type completion.

Important APIs and control flow: for 64-bit SPARC it defines old UID/GID types, signed `__kernel_suseconds_t`, long/ulong aliases, and old timeval layout. For 32-bit SPARC it defines size, ssize, ptrdiff, IPC pid, UID/GID, mode, disk address, and old device types. Generic POSIX types are included afterward.

State, dependencies, and risks: no runtime state, but the typedefs determine UAPI structure layout. Dependencies include compiler ABI macros and `asm-generic/posix_types.h`. Risks are namespace pollution, libc incompatibility, and subtle layout drift in IPC, stat, signal, and socket time structures. Test signals are userspace header builds and ABI layout assertions for both SPARC modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/posix_types.h -->
