<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/posix_types_32.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/posix_types_32.h

Purpose: Defines i386-specific POSIX kernel types before falling back to generic POSIX types.

Important APIs/types/functions: Typedefs for `__kernel_mode_t`, `__kernel_ipc_pid_t`, `__kernel_uid_t`, `__kernel_gid_t`, and `__kernel_old_dev_t`, plus inclusion of `asm-generic/posix_types.h`.

Control flow: No runtime flow.

State and persistence behavior: No state. Typedef widths persist as i386 UAPI ABI.

Dependencies and integration points: Integrates with 32-bit SysV IPC, stat, file mode, UID/GID, and old device number layouts.

Risks and test signals: Risks are width changes that break 32-bit binaries. Test i386 userspace header compilation and ABI size checks for IPC/stat structures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/posix_types_32.h -->
