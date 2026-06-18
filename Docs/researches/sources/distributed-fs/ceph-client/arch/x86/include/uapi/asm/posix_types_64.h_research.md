<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/posix_types_64.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/posix_types_64.h

Purpose: Defines x86_64-specific old UID/GID and old device types before generic POSIX type definitions.

Important APIs/types/functions: Typedefs for `__kernel_old_uid_t`, `__kernel_old_gid_t`, and `__kernel_old_dev_t`, plus inclusion of `asm-generic/posix_types.h`.

Control flow: No runtime flow.

State and persistence behavior: No state. Typedef widths persist as x86_64 UAPI ABI.

Dependencies and integration points: Integrates with x86_64 stat, IPC, and legacy UID/GID/device interfaces.

Risks and test signals: Risks are layout changes affecting old ABI fields. Test x86_64 userspace compilation and struct layout assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/posix_types_64.h -->
