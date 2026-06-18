# sources/distributed-fs/ceph-client/arch/arm/include/asm/suspend.h

## Purpose
Declares ARM CPU suspend state structures and low-level suspend/resume entry points.

## Important APIs, Types, And Functions
Key declarations include struct sleep_save_sp {; extern void cpu_resume(void);; extern void cpu_resume_no_hyp(void);; extern void cpu_resume_arm(void);; extern int cpu_suspend(unsigned long, int (*)(unsigned long));; extern void __cpu_suspend_save(u32 *ptr, u32 ptrsz, u32 sp, u32 *save_ptr);. Important macros/constants include __ASM_ARM_SUSPEND_H. It depends directly on #include <linux/types.h>.

## Control Flow
Power-management code saves CPU context, calls firmware/platform suspend, then resumes through cpu_resume and restore helpers.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include #include <linux/types.h>.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
