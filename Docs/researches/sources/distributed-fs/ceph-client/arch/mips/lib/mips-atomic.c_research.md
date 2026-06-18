# sources/distributed-fs/ceph-client/arch/mips/lib/mips-atomic.c

Purpose: implements local IRQ disable/save/restore for MIPS CPUs lacking the `di/ei` instruction support selected by `CONFIG_CPU_HAS_DIEI`.

Important APIs/functions: exports `arch_local_irq_disable`, `arch_local_irq_save`, and `arch_local_irq_restore`.

Control flow: each function disables preemption for the notrace sequence, manipulates CP0 Status IE bits via inline assembly, applies IRQ hazard barriers, and reenables preemption. Save returns prior Status; restore merges requested IE state back into CP0 Status.

State and persistence: mutates CP0 Status interrupt-enable state.

Dependencies and integration: used by low-level IRQ flag helpers and fallback bitops; depends on CP0 hazards and TX49 errata comments.

Risks: inline assembly must preserve only intended Status bits and respect hazards. Incorrect restore can enable interrupts too early or lose exception-level bits.

Test signals: IRQ enable/disable nesting tests, lockdep/interrupt tracing sanity, affected CPU boot tests, and preemption notrace validation.
