<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/posix_types.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/posix_types.h

Purpose: defines Xtensa UAPI kernel POSIX base types before deferring to generic definitions. Important typedefs are `__kernel_ipc_pid_t`, `__kernel_size_t`, `__kernel_ssize_t`, `__kernel_ptrdiff_t`, `__kernel_old_uid_t`, `__kernel_old_gid_t`, and `__kernel_old_dev_t`.

Control flow is none; it is exported ABI type definition. Persistent state impacted is binary layout of UAPI structures using these typedefs. Dependencies include `asm-generic/posix_types.h` and non-GCC userspace compatibility concerns. Integration points are libc, SysV IPC, stat/signal/ioctl layouts, and headers_install. Risks are type-size ABI breakage, namespace pollution, and compiler compatibility. Test signals include userspace header compile tests, ABI size/offset checks, libc builds, and IPC/stat structure validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/posix_types.h -->
