# sources/distributed-fs/ceph-client/lib/irq_regs.c

Purpose: provides the generic per-CPU saved IRQ register pointer storage for architectures that do not define their own IRQ register handling.

Important APIs/types: defines and exports per-CPU `struct pt_regs *__irq_regs` unless `ARCH_HAS_OWN_IRQ_REGS` is set.

Control flow: no runtime functions; compilation creates per-CPU storage and export metadata.

State and persistence: persistent per-CPU pointer state tracks the current interrupt register frame as maintained by architecture/common IRQ code.

Dependencies and integration: depends on percpu support, export macros, and `asm/irq_regs.h`. Consumers use the exported per-CPU symbol to retrieve or set IRQ context registers.

Risks: only suitable when architecture semantics match the generic pointer model; incorrect updates elsewhere can expose stale register context.

Test signals: architecture build coverage without `ARCH_HAS_OWN_IRQ_REGS`; interrupt entry/exit tracing and oops diagnostics that rely on current IRQ regs.
