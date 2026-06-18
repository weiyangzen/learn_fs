<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/statfs.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/statfs.h

Purpose: Defines x86-specific packing for compat `statfs64` before including generic statfs definitions.

Important APIs/types/functions: `ARCH_PACK_COMPAT_STATFS64` and inclusion of `asm-generic/statfs.h`.

Control flow: Filesystem statfs syscalls copy generic structures, with packed compat layout for i386 ABI expectations.

State and persistence behavior: No state. Structures serialize filesystem capacity and ID metadata.

Dependencies and integration points: Integrates with VFS statfs, compat syscalls, libc, and generic statfs UAPI.

Risks and test signals: Risks include compat packing mismatch between i386 and x86_64. Test `statfs64` from 32-bit userspace on 64-bit kernels and ABI size/alignment checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/statfs.h -->
