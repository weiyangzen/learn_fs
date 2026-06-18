<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-tb10x.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-tb10x.c

Purpose: implements the Abilis TB10x GPIO controller using the generic GPIO library, with optional edge-both interrupt-controller support.

Important APIs, types, and functions: `struct tb10x_gpio` holds MMIO base, optional IRQ domain, parent IRQ, and `gpio_generic_chip`. `tb10x_gpio_to_irq()` maps GPIO offsets into a linear IRQ domain. `tb10x_gpio_irq_set_type()` accepts only `IRQ_TYPE_EDGE_BOTH`. `tb10x_gpio_irq_cascade()` dispatches enabled change bits. Probe configures generic GPIO registers for data and direction.

Control flow: probe requires an OF node and `abilis,ngpio`, maps MMIO, initializes a generic chip, overrides `ngpio` and request/free callbacks, registers the gpiochip, and, when `interrupt-controller` is present, requests the parent IRQ, creates a linear domain, allocates a generic IRQ chip, and binds ack/mask registers. Remove tears down the generic IRQ chip and domain.

State and persistence behavior: direction/data state lives in controller registers. IRQ mask and pending bits live in hardware/generic irqchip state. No PM state is saved.

Dependencies and integration points: depends on OF, `gpio_generic_chip_init()`, gpiolib, irqdomain generic-chip helpers, and a parent interrupt line.

Risks and test signals: `BIT(ngpio) - 1` in removal assumes `ngpio` is representable in an unsigned long bit mask; large or invalid DT values are risky. Only both-edge interrupts are supported despite generic Linux IRQ type APIs. Test GPIO register access, DT `ngpio`, no-interrupt mode, parent IRQ sharing, change-register acking, mask behavior, and invalid IRQ type rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-tb10x.c -->
