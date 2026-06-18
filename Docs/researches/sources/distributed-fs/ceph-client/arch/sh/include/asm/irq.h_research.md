<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/irq.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/irq.h

## Purpose
Defines SH architecture declarations and macros for `irq` support in the Ceph client's vendored Linux source tree.

## Important APIs, Types, And Functions
Includes `linux/cpumask.h`, `asm/machvec.h`, `asm-generic/irq.h`. Key macros/constants include `__ASM_SH_IRQ_H`, `NO_IRQ_IGNORE`, `irq_demux(irq)`, `irq_ctx_init(cpu)`, `irq_ctx_exit(cpu)`, `irq_lookup(irq)`, `irq_finish(irq)`. Functions or extern declarations include `make_imask_irq`, `init_IRQ`, `migrate_irqs`, `irq_ctx_init`, `irq_ctx_exit`, `irq_lookup`, `irq_finish`. Register or hardware-address constants include `__ASM_SH_IRQ_H`, `NO_IRQ_IGNORE`.

## Control Flow
Runtime flow is driven by traps, syscalls, context switches, futex atomics, IRQ entry, and scheduler transitions. These headers define register conventions, inline assembly, and selected backends that low-level SH assembly and generic kernel code call.

## State And Persistence
State lives in `pt_regs`, `thread_info`, task thread structs, syscall registers, lock words, futex user words, IRQ flags, and status registers. Inline assembly must preserve those layouts exactly across entry and switch paths.

## Dependencies And Integration Points
It directly depends on `linux/cpumask.h`, `asm/machvec.h`, `asm-generic/irq.h`. Kconfig-sensitive paths mention `CONFIG_IRQSTACKS`, `CONFIG_INTC_BALANCING`. Integration points are low-level entry assembly, scheduler context switching, syscall tracing, futex/locking code, and IRQ/trap handling.

## Risks And Edge Cases
Risks include register convention drift, clobbered `pt_regs`, incorrect syscall argument mapping, incomplete exception fixups, lock/futex atomicity loss, and SMP configurations selecting unsupported primitives.

## Test Signals
Useful signals are syscall tracing tests, ptrace/audit/seccomp checks, futex stress, lock torture, IRQ tracing, context-switch stress, and boot tests with SMP and non-SMP configs.

Source read size: 51 lines, 1185 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/irq.h -->
