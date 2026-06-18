# sources/distributed-fs/ceph-client/drivers/mfd/max8997-irq.c

Purpose: Nested interrupt-controller support for MAX8997/MAX8966 PMIC functions. It groups PMIC, MUIC, GPIO, flash, and placeholder fuel-gauge interrupt sources, keeps per-group masks, and dispatches logical IRQs through an irqdomain.

Important APIs, types, and functions: `max8997_mask_reg[]` maps interrupt groups to mask registers. `get_i2c()` selects the PMIC or MUIC client per group. `struct max8997_irq_data` and `max8997_irqs[]` map child hwirqs to group masks. `max8997_irq_thread()` reads `MAX8997_REG_INTSRC`, pulls only asserted group status registers, synthesizes GPIO edge status from `GPIOCNTL` values, applies `irq_masks_cur`, and calls `handle_nested_irq()`. `max8997_irq_init()` initializes masks, samples GPIO baseline state, creates a linear irqdomain, and requests the primary and optional ONO IRQs. `max8997_irq_resume()` replays pending IRQ processing after resume.

Control flow: the parent driver calls `max8997_irq_init()` after dummy I2C clients are available. Child drivers mask/unmask through the irq chip, and the bus sync callback writes all valid group masks to hardware. The threaded parent IRQ fans out to mapped nested IRQs; resume invokes the same fanout path to handle latched sleep events.

State and persistence: `irq_masks_cur`, `irq_masks_cache`, `gpio_status`, `irq_domain`, and `irqlock` live in `struct max8997_dev`. Hardware masks persist in PMIC and MUIC registers. GPIO edge detection depends on the saved baseline sampled at IRQ init.

Dependencies and integration points: uses register helpers from `max8997.c`, definitions from `max8997-private.h`, the IRQ core, and the MUIC dummy client. It exposes the IRQ domain consumed indirectly by MFD child resources.

Risks: fuel-gauge interrupt relay is explicitly unimplemented. GPIO baseline handling appears to store boolean values but compares against raw register bytes, which can over-detect changes. `max8997_irq_init()` creates an irqdomain but does not remove it on request-IRQ failure. `max8997_irq_sync_unlock()` writes masks unconditionally, even if cache values did not change. Test signals include PMIC and MUIC interrupt fanout, ONO IRQ edge handling, GPIO rise/fall/both semantics, resume latch replay, and error injection for I2C status reads.
