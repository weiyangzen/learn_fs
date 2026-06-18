
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-ge.c

Purpose: supports GE FPGA-based GPIO blocks on several GE boards with a simple big-endian generic MMIO gpiochip.

Important APIs/types/functions: `gef_gpio_probe()` is the only substantive function. It uses `struct gpio_generic_chip_config`, `struct gpio_generic_chip`, and OF match data to set the number of GPIO lines for `gef,sbc610-gpio`, `gef,sbc310-gpio`, and `ge,imp3a-gpio`.

Control flow: probe allocates a generic chip, maps one MMIO resource, initializes generic GPIO with input data, output set, and direction-input registers using big-endian byte order, labels the chip from the fwnode, sets dynamic base, applies match-data `ngpio`, and registers the chip. Registration uses `module_platform_driver_probe()` for one-shot probe behavior.

State and persistence behavior: the driver has no private state after registration; GPIO state persists in FPGA registers. There is no IRQ configuration in this driver even though the hardware has trigger/polarity/status registers.

Dependencies and integration points: depends on OF match data, platform MMIO resources, gpiolib generic helpers, and big-endian register access.

Risks: interrupt support is explicitly left as TODO; hardware interrupts may be generated but masking is delegated to external interrupt controllers. Output mode configuration is also unsupported. Register semantics depend on the generic helper matching GE FPGA layout.

Test signals: compatible-specific line counts, big-endian generic register access, input/output/direction operation, probe failure on missing resource, and absence of IRQ chip registration.
