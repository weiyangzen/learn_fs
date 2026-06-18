
# sources/distributed-fs/ceph-client/arch/x86/include/asm/compat.h

Purpose: x86 32-bit and x32 compatibility ABI types and syscall-mode helpers.

Important APIs and control flow: defines compat uid/gid/mode/dev/ipc types, `compat_stat`, packed flock64 need, `compat_statfs`, and `COMPAT_UTS_MACHINE`. `in_x32_syscall()` checks the x32 syscall bit when enabled; `in_32bit_syscall()` combines IA32 and x32; `in_compat_syscall()` overrides the generic implementation under `CONFIG_COMPAT`. x32 may override siginfo copying.

State, dependencies, and risks: state comes from current task registers and syscall number bits. Dependencies include generic compat ABI, processor/user32 definitions, and syscall numbering. Risks include struct layout drift from userspace ABI, incorrect x32/IA32 classification, and time/alignment differences. Test signals are compat syscall tests, x32 ABI tests, stat/statfs layout checks, and ptrace/signal compat tests.
