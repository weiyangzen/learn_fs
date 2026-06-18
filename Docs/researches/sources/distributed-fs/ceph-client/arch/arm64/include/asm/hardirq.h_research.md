## sources/distributed-fs/ceph-client/arch/arm64/include/asm/hardirq.h

Purpose: defines arm64 hard IRQ accounting structures and stack helpers.

Important APIs/types/functions: declares per-CPU IRQ stack state, `ack_bad_irq`, hardirq stat fields, and irq-stack access helpers depending on configuration.

Control flow: IRQ entry may switch to a per-CPU IRQ stack and update hardirq accounting; bad IRQs are reported through the architecture hook.

State and persistence: per-CPU IRQ stack pointers and IRQ statistics persist during runtime.

Dependencies and integration: used by generic IRQ entry, interrupt handling, stack unwinding, and `/proc/interrupts` accounting.

Risks: stack switching bugs cause hard-to-debug crashes under interrupt load. Test signals are interrupt storm tests, lockdep IRQ state checks, stack unwinder tests, and bad-IRQ injection.
