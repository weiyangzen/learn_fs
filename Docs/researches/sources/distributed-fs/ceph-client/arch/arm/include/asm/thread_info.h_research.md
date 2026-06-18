# sources/distributed-fs/ceph-client/arch/arm/include/asm/thread_info.h

## Purpose
Defines ARM low-level thread_info, saved CPU register context, thread flag bits, syscall-work masks, stack sizing, and VFP/IWMMXT task-state hooks.

## Important APIs, Types, And Functions
Key declarations include struct task_struct;; struct cpu_context_save {; struct thread_info {; unsigned long flags; /* low level flags */; struct cpu_context_save cpu_context; /* cpu context */; unsigned long tp_value[2]; /* TLS registers */. Important macros/constants include __ASM_ARM_THREAD_INFO_H, THREAD_SIZE_ORDER, THREAD_SIZE_ORDER, THREAD_SIZE, THREAD_START_SP, THREAD_ALIGN, THREAD_ALIGN, OVERFLOW_STACK_SIZE, INIT_THREAD_INFO(tsk), thread_saved_pc(tsk). It depends directly on #include <linux/compiler.h>, #include <asm/fpstate.h>, #include <asm/page.h>, #include <asm/types.h>, #include <asm/traps.h>.

## Control Flow
Entry assembly and scheduler code access fixed offsets in thread_info, while signal/FPU code preserves or restores VFP/IWMMXT state around task switches and user transitions.

## State And Persistence
State persists per task in thread_info: flags, preempt count, CPU number, domain, saved CPU context, TLS values, and floating-point/copressor state.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include #include <linux/compiler.h>, #include <asm/fpstate.h>, #include <asm/page.h>, #include <asm/types.h>, #include <asm/traps.h>.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
