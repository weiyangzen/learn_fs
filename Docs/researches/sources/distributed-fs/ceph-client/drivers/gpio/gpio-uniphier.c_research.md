<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-uniphier.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-uniphier.c

Purpose: implements Socionext UniPhier GPIO with banked MMIO GPIO operations, hierarchical IRQs through the parent AIDET interrupt controller, both-edge support via noise filter hardware, and late suspend/resume state save.

Important APIs, types, and functions: `struct uniphier_gpio_priv` contains gpiochip, irq_chip, child irqdomain, MMIO base, spinlock, and flexible saved register array. GPIO callbacks are get_direction, direction_input, direction_output, get, set, set_multiple, and `to_irq()`. IRQ domain callbacks allocate parent IRQs using `socionext,interrupt-ranges`, activate/deactivate gpiochip IRQ locks, and translate fwspecs.

Control flow: probe locates the parent IRQ domain, reads `ngpios`, allocates enough saved-register slots, maps MMIO, fills gpiochip and irq_chip operations, initializes filter cycle count, registers the gpiochip, creates a hierarchical IRQ domain, and stores drvdata. `to_irq()` only maps offsets at or above `UNIPHIER_GPIO_IRQ_OFFSET`. IRQ set_type enables both-edge mode and filter bits locally, then programs the parent as falling-edge for both-edge mode.

State and persistence behavior: hardware stores data, direction, IRQ enable/mode/filter. Suspend saves per-bank data/direction plus IRQ control registers; resume restores them and reinitializes filter cycle count.

Dependencies and integration points: depends on DT binding constants, parent OF IRQ domain, `socionext,interrupt-ranges`, gpiolib, irqdomain hierarchy, and late system sleep PM ops.

Risks and test signals: interrupt range parsing is mandatory for IRQ allocation; incorrect ranges break `to_irq()`. Both-edge mode depends on a shared noise filter period, not per-line debounce. Test ngpio bank calculations, non-contiguous register offsets, set_multiple clumps, IRQ offset gating, parent mapping ranges, both-edge/filter behavior, and suspend/resume restoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-uniphier.c -->
