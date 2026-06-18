# sources/distributed-fs/ceph-client/drivers/irqchip/irq-aspeed-intc.c

Purpose: Implements the Aspeed AST2700 interrupt controller as a 32-source chained irqchip with enable/status registers.

Important APIs/types/functions: `struct aspeed_intc_ic`, `aspeed_intc_ic_irq_handler()`, `aspeed_intc_irq_mask()`, `aspeed_intc_irq_unmask()`, `aspeed_intc_ic_map_irq_domain()`, and `aspeed_intc_ic_of_init()`.

Control flow: Init maps registers, clears all pending status bits, disables all enables, creates a 32-entry domain, initializes raw spinlocks, validates every parent IRQ in the DT node, then chains the same handler to each parent. The handler reads status under `gic_lock`, dispatches each set child bit, and writes the bit back to clear status.

State and persistence: Persistent state includes base, two raw spinlocks, and the IRQ domain. Hardware state consists of enable bits and write-one-to-clear status bits.

Dependencies/integration: Uses OF IRQ parsing, chained IRQ handling, raw spinlocks, irqdomain, MMIO, and level child handlers.

Risks and test signals: Mask/unmask reads occur before taking `intc_lock`, so concurrent RMW races should be reviewed. Test multiple parent IRQs, all 32 child bits, status clearing after child handling, init failure cleanup after mapped parent IRQs, and lock ordering.
