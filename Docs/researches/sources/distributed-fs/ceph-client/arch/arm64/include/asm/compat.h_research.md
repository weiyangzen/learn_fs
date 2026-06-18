## sources/distributed-fs/ceph-client/arch/arm64/include/asm/compat.h

Purpose: defines AArch32 compatibility ABI types and helpers for an arm64 kernel.

Important APIs/types/functions: defines 16-bit compat uid/gid/mode/pid types, `struct compat_stat`, `struct compat_statfs`, `COMPAT_UTS_MACHINE`, `compat_user_stack_pointer`, `COMPAT_MINSIGSTKSZ`, `is_compat_task`, `is_compat_thread`, and `compat_arm_syscall`.

Control flow: helpers test `TIF_32BIT` on current task or a supplied thread. Compat syscall handling is implemented elsewhere.

State and persistence: reads thread flags and task register state; structure layouts define persistent userspace ABI for compat stat/statfs.

Dependencies and integration: depends on generic compat definitions, task stack helpers, ptrace regs, and syscall/ELF handling.

Risks: layout or flag changes break 32-bit userspace ABI. Test signals are compat LTP, 32-bit libc/syscall tests, stat/statfs ABI checks, and mixed 32/64-bit process tracing.
