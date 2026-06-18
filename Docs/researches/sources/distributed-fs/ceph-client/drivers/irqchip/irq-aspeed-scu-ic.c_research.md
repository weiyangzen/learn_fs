# sources/distributed-fs/ceph-client/drivers/irqchip/irq-aspeed-scu-ic.c

Purpose: Implements Aspeed SCU interrupt controllers across AST24xx/25xx/26xx/27xx variants, handling combined enable/status registers and split IER/ISR layouts.

Important APIs/types/functions: `struct aspeed_scu_ic_variant`, `struct aspeed_scu_ic`, combined/split IRQ handlers, combined/split mask/unmask callbacks, `aspeed_scu_ic_map()`, `aspeed_scu_ic_find_variant()`, and `aspeed_scu_ic_of_init()`.

Control flow: Init finds variant metadata from the compatible string, maps registers, clears pending status and disables enable bits according to combined or split layout, maps the parent IRQ, creates a linear child domain sized by variant `num_irqs`, and chains the correct handler. Handlers compute enabled pending bits with variant shift/mask and dispatch child hwirqs, then clear the hardware status bit.

State and persistence: Runtime state stores enable mask, shift, number of IRQs, base, domain, and IER/ISR offsets. Hardware state persists in SCU enable/status registers and is variant-dependent.

Dependencies/integration: Uses OF, chained IRQs, irqdomain, bit helpers, and MMIO. It returns `-EINVAL` for affinity changes because the SCU fan-out has no CPU targeting.

Risks and test signals: Test all variant compatibles, especially AST2700 split register offsets; verify write-one-to-clear operations do not accidentally clear unrelated combined status bits; test shifted IRQ ranges, parent storms, and error cleanup after mapping failures.
