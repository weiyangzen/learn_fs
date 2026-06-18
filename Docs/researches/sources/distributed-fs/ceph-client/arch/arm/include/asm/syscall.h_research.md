# sources/distributed-fs/ceph-client/arch/arm/include/asm/syscall.h

## Purpose
Defines ARM syscall inspection and mutation helpers for tracing, audit, seccomp, and restart handling.

## Important APIs, Types, And Functions
Key declarations include extern const unsigned long sys_call_table[];; static inline int syscall_get_nr(struct task_struct *task,; struct pt_regs *regs); static inline bool __in_oabi_syscall(struct task_struct *task); static inline bool in_oabi_syscall(void); static inline void syscall_rollback(struct task_struct *task,. Important macros/constants include _ASM_ARM_SYSCALL_H, NR_syscalls. It depends directly on #include <uapi/linux/audit.h> /* for AUDIT_ARCH_* */, #include <linux/elf.h> /* for ELF_EM */, #include <linux/err.h>, #include <linux/sched.h>, #include <asm/unistd.h>.

## Control Flow
Entry code populates pt_regs; tracing code reads syscall numbers/arguments, changes return values, and identifies ABI variants through these helpers.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include #include <uapi/linux/audit.h> /* for AUDIT_ARCH_* */, #include <linux/elf.h> /* for ELF_EM */, #include <linux/err.h>, #include <linux/sched.h>, #include <asm/unistd.h>.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
