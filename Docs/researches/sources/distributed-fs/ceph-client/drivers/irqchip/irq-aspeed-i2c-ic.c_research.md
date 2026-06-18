# sources/distributed-fs/ceph-client/drivers/irqchip/irq-aspeed-i2c-ic.c

Purpose: Implements the Aspeed AST2400/AST2500 I2C interrupt fan-out controller, converting one parent interrupt into per-bus child interrupts.

Important APIs/types/functions: `struct aspeed_i2c_ic`, `aspeed_i2c_ic_irq_handler()`, `aspeed_i2c_ic_map_irq_domain()`, `aspeed_i2c_ic_of_init()`, and two `IRQCHIP_DECLARE` compatibles.

Control flow: Init allocates state, maps one MMIO register, maps the parent IRQ, creates a 14-entry linear domain, names it, and installs a chained parent handler. The handler reads the status word and dispatches every set bit to the child domain with a dummy irqchip/simple handler.

State and persistence: State is only base address, parent IRQ, and IRQ domain. The hardware status register is read but not explicitly acknowledged here, implying child I2C controllers likely clear their own conditions.

Dependencies/integration: Uses OF address/IRQ parsing, chained IRQ helpers, irqdomain, `dummy_irq_chip`, and generic child IRQ handling.

Risks and test signals: Test status bits for all 14 buses, parent interrupt clearing semantics, missing parent IRQ cleanup, domain host data being NULL despite `irq_set_chip_data()`, and interrupt storms if child handlers do not clear source status.
