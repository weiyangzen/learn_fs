# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/intc-shx3.c

Purpose: supplies shared SH-X3 interrupt-controller glue that is not tied to a single interrupt vector table. It registers the user interrupt mask register and, when balancing is enabled, provides acknowledge/finish helpers for the SH-X3 interrupt-distribution path.

Important APIs, types, and functions: `shx3_irq_setup()` calls `register_intc_userimask(INTC_USERIMASK)` at `arch_initcall`. Under `CONFIG_INTC_BALANCING`, `irq_lookup()` samples `INTACK` and returns either the IRQ or `NO_IRQ_IGNORE`, while `irq_finish()` writes `irq2evt(irq)` to `INTACKCLR`.

Control flow: early interrupt setup from SoC-specific `setup-shx3.c` registers the main descriptors; this file later registers the user mask at `0xfe411000`. Balanced interrupt handling calls the lookup and finish hooks around dispatched interrupts.

State and persistence: no heap state is kept. Persistent behavior is in MMIO registers `INTACK`, `INTACKCLR`, and `INTC_USERIMASK`.

Dependencies and integration points: depends on `<linux/irq.h>`, `<linux/io.h>`, and SuperH INTC helper APIs. It complements `setup-shx3.c`, `setup-sh7786.c`, and other INTC descriptors that use SMP balancing macros.

Risks: the balancing helpers assume the acknowledgement register protocol and event-code mapping match the active SH-X3 interrupt controller. Misordered ack/clear writes can lose interrupts. `irq_lookup()` masks on bit 0 only, so behavior depends on undocumented hardware semantics.

Test signals: with `CONFIG_INTC_BALANCING`, multi-CPU interrupt routing should deliver interrupts once and clear them; `/proc/interrupts` should increment on expected CPUs; boot should not warn about user-imask registration failure.
