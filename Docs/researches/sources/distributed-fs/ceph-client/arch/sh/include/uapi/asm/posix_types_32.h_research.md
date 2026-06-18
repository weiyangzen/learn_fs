<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/posix_types_32.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/posix_types_32.h

Purpose: defines 32-bit SH kernel POSIX base types.

Important APIs/types/functions: `__kernel_mode_t`, pid/ipc ids, uid/gid old types, old dev type, and generic posix include handoff.

Control flow: userspace sees these typedefs through installed headers.

State and persistence: no runtime state.

Dependencies/integration: integrates with generic `asm-generic/posix_types.h` and libc.

Risks: type-width changes are ABI breaks for syscalls and file formats.

Test signals: run UAPI type-size checks against known SH ABI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/posix_types_32.h -->
