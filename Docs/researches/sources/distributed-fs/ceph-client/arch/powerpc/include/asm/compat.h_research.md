## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/compat.h

Purpose: defines PowerPC 32-bit compatibility ABI types and layouts used by a 64-bit kernel servicing 32-bit tasks.

Important APIs/types/functions: exports `COMPAT_UTS_MACHINE`, `compat_ipc_pid_t`, `compat_nlink_t`, `struct compat_stat`, `struct compat_ipc64_perm`, `compat_semid64_ds`, `compat_msqid64_ds`, `compat_shmid64_ds`, and `is_compat_task()`.

Control flow: there is no runtime algorithm beyond `is_compat_task()` delegating to `is_32bit_task()`. The rest are ABI layout definitions for compat syscall marshaling.

State and persistence: no kernel-owned state. The structures persist as userspace ABI contracts for stat and SysV IPC data exchanged across syscall boundaries.

Dependencies and integration: includes generic compat definitions, Linux types, scheduler/task mode helpers, and endian-specific UTS machine strings (`ppc` or `ppcle`). It integrates with compat syscall handlers, ELF personality, and IPC/stat copy routines.

Risks and test signals: field order, width, padding, and time high/low halves are ABI-sensitive. Any layout change can break 32-bit userspace on 64-bit kernels. Test signals include 32-bit PowerPC userspace under a 64-bit kernel, LTP compat syscall tests, stat and SysV IPC tests, endian-specific builds, and ABI structure size checks.
