# sources/distributed-fs/ceph-client/arch/m68k/coldfire/intc-525x.c

Purpose: second interrupt-controller GPIO IRQ support for MCF525x, where rising and falling edge enables/clears occupy separate bit banks.

Important APIs and functions: `intc2_irq_gpio_mask()`, `intc2_irq_gpio_unmask()`, `intc2_irq_gpio_ack()`, `intc2_irq_gpio_set_type()`, `intc2_irq_gpio_chip`, and `mcf_intc2_init()`.

Control flow and state: `mcf_intc2_init()` writes `MCFINTC2_VECBASE` to `MCFINTC2_INTBASE`, then installs edge handlers for GPIO0-GPIO6. Mask/unmask/ack inspect `irqd_get_trigger_type()` and clear/set low bits for rising and high bits (`0x100 << irq`) for falling. `set_type` accepts only `IRQ_TYPE_EDGE_BOTH` subsets.

Dependencies and integration: Linux IRQ core, trigger-type metadata, and MCF525x SIM2/INTC2 registers. It runs alongside the primary ColdFire interrupt controller and gpiolib mapping.

Risks and test signals: if clients never call `irq_set_irq_type()`, the type mask may be zero and mask/unmask/ack do nothing. The callback validates but does not program a separate polarity register, implying GPIOINTENABLE itself selects edges. Test rising-only, falling-only, and both-edge GPIO interrupts, including ack behavior and vector-base setup.
