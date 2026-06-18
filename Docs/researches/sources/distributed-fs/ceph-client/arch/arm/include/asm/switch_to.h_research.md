# sources/distributed-fs/ceph-client/arch/arm/include/asm/switch_to.h

## Purpose
Defines the ARM context-switch macro that invokes __switch_to with previous and next task/thread state.

## Important APIs, Types, And Functions
Key declarations include extern struct task_struct *__switch_to(struct task_struct *, struct thread_info *, struct thread_info *);. Important macros/constants include __ASM_ARM_SWITCH_TO_H, __complete_pending_tlbi(), __complete_pending_tlbi(), switch_to(prev,next,last). It depends directly on #include <linux/thread_info.h>, #include <asm/smp_plat.h>.

## Control Flow
The scheduler calls switch_to; low-level assembly saves callee-saved registers and restores the next task cpu_context.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include #include <linux/thread_info.h>, #include <asm/smp_plat.h>.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
