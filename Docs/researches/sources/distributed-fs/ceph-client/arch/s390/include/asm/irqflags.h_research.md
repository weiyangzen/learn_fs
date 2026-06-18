# sources/distributed-fs/ceph-client/arch/s390/include/asm/irqflags.h

Purpose: This header implements s390 local interrupt flag save, disable, enable, restore, and query primitives.

Important APIs/types/functions: `ARCH_IRQ_ENABLED`, `__arch_local_irq_stosm()`, `__arch_local_irq_stnsm()`, `__arch_local_irq_ssm()`, `arch_local_save_flags()`, `arch_local_irq_save()`, `arch_local_irq_disable()`, `arch_local_irq_enable_external()`, `arch_local_irq_enable()`, `arch_local_irq_restore()`, `arch_irqs_disabled_flags()`, and `arch_irqs_disabled()` are defined.

Control flow: The helpers use `stosm`, `stnsm`, and `ssm` to read and modify the system mask. Save/disable clears external and I/O interrupt enable bits, enable sets external or both external/I/O bits, and restore only transitions from disabled to the saved enabled state.

State and persistence: Persistent state is the current CPU PSW/system-mask interrupt enable bits. Under KMSAN, functions gain noinline/notrace/no-sanitize attributes to avoid instrumentation recursion.

Dependencies and integration points: It depends on Linux types, PSW/system mask semantics, KMSAN configuration, and generic irqflags consumers across scheduler, locking, and MM context switching.

Risks and test signals: Incorrect mask constants can globally enable or suppress interrupts. Tests should cover lockdep IRQ state, nested save/restore, external-only enable users, KMSAN builds, context switch paths, and interrupt delivery after local_irq_enable.
