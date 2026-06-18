<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/posix_types.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/posix_types.h

Source read size: 24 lines, 639 bytes.

Purpose: defines PA-RISC-specific kernel POSIX scalar types before generic type completion. Important APIs: 32-bit `__kernel_mode_t`, `__kernel_ipc_pid_t`, `__kernel_off64_t`, and `__kernel_ino64_t`. Control flow: no runtime flow; headers use these typedefs when compiling userspace interfaces. State and persistence: compile-time ABI type sizes. Dependencies and integration points: generic posix types, stat/IPС/socket headers, libc. Risks: type-size drift changes structure layouts and syscall ABI. Test signals: headers_install, libc type conformance, stat/IPC structure layout tests on 32-bit and 64-bit builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/posix_types.h -->
