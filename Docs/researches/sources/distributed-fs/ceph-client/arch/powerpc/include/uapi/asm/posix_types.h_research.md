<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/posix_types.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/posix_types.h

Purpose: Defines PowerPC-specific POSIX base type overrides before generic POSIX types.

Important APIs/types/functions: On ppc64 `__kernel_old_dev_t` is unsigned long; on ppc32 `__kernel_ipc_pid_t` is short.

Control flow: Compile-time ABI type selection occurs before including generic posix types.

State and persistence: No runtime state; affects structure layout and syscall ABI.

Dependencies and integration points: Used by generic POSIX UAPI headers and libc.

Risks: Type width changes break stat, IPC, and legacy device-number ABI.

Test signals: Headers compile for ppc32/ppc64 and libc layout conformance checks.

Source read size: 21 lines, 594 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/posix_types.h -->
