# sources/distributed-fs/ceph-client/arch/s390/include/asm/irq.h

Purpose: This header defines s390 architectural IRQ numbers, external interruption codes, per-class IRQ statistics, and external interrupt registration APIs.

Important APIs/types/functions: `EXT_INTERRUPT`, `IO_INTERRUPT`, `THIN_INTERRUPT`, external code constants, `enum interruption_class`, `struct irq_stat`, per-CPU `irq_stat`, `inc_irq_stat()`, `struct ext_code`, `ext_int_handler_t`, `register_external_irq()`, `unregister_external_irq()`, `enum irq_subclass`, and `irq_subclass_register/unregister()` are the main definitions.

Control flow: Low-level interrupt handlers classify external, I/O, thin, NMI, and restart events, increment per-class counters, and dispatch registered external handlers by interruption code. Subclass registration manipulates control-register masks for selected external subclasses.

State and persistence: Per-CPU IRQ counters persist in `irq_stat`; external-handler tables and subclass reference state live in implementation code. The header establishes only the ABI and constants.

Dependencies and integration points: It depends on hardirq/percpu/cache helpers and control-register masks from `ctlreg.h`, integrating with `/proc/interrupts`, timer, service-signal, IUCV, CIO, DASD, QDIO, PCI MSI, and NMI paths.

Risks and test signals: Interrupt code mismatches or unbalanced subclass registration can mask required events globally. Tests should cover external handler register/unregister, interrupt counter reporting, timer/service/IUCV delivery, PCI/CIO IRQs, and CPU hotplug.
