<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/posix_types_x32.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/posix_types_x32.h

Purpose: Defines x32-specific `long` and `unsigned long` kernel typedefs as 64-bit quantities, then reuses the x86_64 POSIX type definitions.

Important APIs/types/functions: `__kernel_long_t`, `__kernel_ulong_t`, and inclusion of `posix_types_64.h`.

Control flow: No runtime flow.

State and persistence behavior: No state. The typedefs preserve the x32 ABI's hybrid ILP32/userspace with selected 64-bit kernel layout fields.

Dependencies and integration points: Integrates with x32 SysV IPC, stat, signal, and generic POSIX types.

Risks and test signals: Risks include treating x32 as ordinary 32-bit or ordinary 64-bit. Test x32 userspace builds and ABI layout checks for time, IPC, and stat structures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/posix_types_x32.h -->
