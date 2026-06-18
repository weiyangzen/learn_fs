<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/errno.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/errno.h

Purpose: Provides SPARC errno values, including historical SunOS-compatible numbering differences.

Important APIs and control flow: the header defines architecture-specific errno constants and then integrates generic errno definitions. Its values are consumed by syscall return paths, libc, and compatibility layers.

State, dependencies, and risks: no runtime state, but values are ABI state. Dependencies include generic errno headers and userspace libc expectations. Risks are severe if numbers change, because syscall error interpretation changes. Test signals are syscall ABI tests, libc header comparisons, and 32-bit/64-bit compat errno checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/errno.h -->
