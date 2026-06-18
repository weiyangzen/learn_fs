# sources/distributed-fs/ceph-client/drivers/gpio/gpio-mxs.c

Purpose: supports Freescale MXS/i.MX23/i.MX28 GPIO ports that share a parent pinctrl register block, with GPIO value/direction and per-port IRQ domains.

Important APIs/types/functions: `struct mxs_gpio_port` stores shared MMIO base, alias id, parent IRQ, IRQ domain, generic MMIO chip, device id, and both-edge mask. Register macros compute per-port offsets differently for i.MX23 and i.MX28. IRQ functions are `mxs_gpio_set_irq_type()`, `mxs_flip_edge()`, `mxs_gpio_irq_handler()`, `mxs_gpio_set_wake_irq()`, and `mxs_gpio_init_gc()`. GPIO-specific callbacks include `mxs_gpio_to_irq()` and `mxs_gpio_get_direction()`.

Control flow: probe reads the `gpio` alias id, match data, and parent IRQ. It maps the parent node's register region only once through a static `base`, disables interrupts for the port, clears IRQ status, allocates a 32-line legacy IRQ domain, initializes a generic irq_chip with separate level and edge chip types, installs the chained handler, initializes a generic GPIO chip over DIN/DOUT set/clear/DOE registers, assigns fixed base `id * 32`, and registers the chip. IRQ type programming selects level/edge, polarity, and enables either `PIN2IRQ` or `IRQEN`; both-edge is emulated by selecting the opposite edge of the current input and flipping polarity after dispatch.

State and persistence behavior: hardware registers hold GPIO data, direction, IRQ enable, polarity, and status. Both-edge emulation state is tracked in `both_edges`. No suspend/resume save path exists, but wake IRQ support toggles parent IRQ wake.

Dependencies and integration points: depends on OF compatibles `fsl,imx23-gpio` and `fsl,imx28-gpio`, parent OF MMIO mapping, `gpio-mmio`, generic IRQ chips, chained IRQ handling, and legacy fixed GPIO bases.

Risks: the shared static `base` is mapped once and `iounmap(port->base)` is called on probe failure, which can affect later ports if partial initialization fails. Both-edge emulation has the usual polarity-toggle race. Fixed base `id * 32` is legacy and can collide if aliases are wrong. No PM restore means suspend behavior relies on pinctrl block retention.

Test signals: i.MX23 versus i.MX28 register offsets, shared base mapping across multiple ports, generic GPIO get/set/direction, level and edge IRQ chip types, both-edge polarity flipping, parent wake enable/disable, and failure paths around IRQ domain/chip setup.
