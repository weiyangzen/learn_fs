# sources/distributed-fs/ceph-client/arch/arm/include/asm/syscalls.h

## Purpose
Declares ARM-specific syscall entry points not covered by generic syscall prototypes.

## Important APIs, Types, And Functions
Key declarations include struct pt_regs;; asmlinkage int sys_sigreturn(struct pt_regs *regs);; asmlinkage int sys_rt_sigreturn(struct pt_regs *regs);; asmlinkage long sys_arm_fadvise64_64(int fd, int advice,; struct oldabi_stat64;; asmlinkage long sys_oabi_stat64(const char __user * filename,. Important macros/constants include __ASM_SYSCALLS_H. It depends directly on #include <linux/linkage.h>, #include <linux/types.h>.

## Control Flow
The syscall table and compat/OABI paths reference these prototypes during build and entry dispatch.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include #include <linux/linkage.h>, #include <linux/types.h>.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
