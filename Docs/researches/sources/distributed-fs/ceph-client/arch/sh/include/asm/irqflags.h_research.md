<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/irqflags.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/irqflags.h

## Purpose
Implements SH local interrupt flag save, restore, enable, disable, and query helpers around status-register interrupt bits.

## Important APIs, Types, And Functions
Includes `asm-generic/irqflags.h`. Key macros/constants include `__ASM_SH_IRQFLAGS_H`, `ARCH_IRQ_DISABLED`, `ARCH_IRQ_ENABLED`. Register or hardware-address constants include `__ASM_SH_IRQFLAGS_H`, `ARCH_IRQ_DISABLED`, `ARCH_IRQ_ENABLED`.

## Control Flow
Runtime flow is driven by traps, syscalls, context switches, futex atomics, IRQ entry, and scheduler transitions. These headers define register conventions, inline assembly, and selected backends that low-level SH assembly and generic kernel code call.

## State And Persistence
State lives in `pt_regs`, `thread_info`, task thread structs, syscall registers, lock words, futex user words, IRQ flags, and status registers. Inline assembly must preserve those layouts exactly across entry and switch paths.

## Dependencies And Integration Points
It directly depends on `asm-generic/irqflags.h`. Integration points are low-level entry assembly, scheduler context switching, syscall tracing, futex/locking code, and IRQ/trap handling.

## Risks And Edge Cases
Risks include register convention drift, clobbered `pt_regs`, incorrect syscall argument mapping, incomplete exception fixups, lock/futex atomicity loss, and SMP configurations selecting unsupported primitives.

## Test Signals
Useful signals are syscall tracing tests, ptrace/audit/seccomp checks, futex stress, lock torture, IRQ tracing, context-switch stress, and boot tests with SMP and non-SMP configs.

Source read size: 10 lines, 226 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/irqflags.h -->
