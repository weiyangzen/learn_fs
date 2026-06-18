
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-da9055.c

Purpose: supports the three GPIO pins of Dialog DA9055 PMICs using MFD register access and regmap IRQ mapping.

Important APIs/types/functions: `struct da9055_gpio` contains the DA9055 parent and gpiochip. Important functions are `da9055_gpio_get()`, `da9055_gpio_set()`, `da9055_gpio_direction_input()`, `da9055_gpio_direction_output()`, `da9055_gpio_to_irq()`, and `da9055_gpio_probe()`. `reference_gp` is the gpiochip template.

Control flow: probe obtains parent `struct da9055`, optional platform data, copies the template, applies legacy base if present, and registers the chip. Direction bits are stored as two-bit fields in paired GPIO registers. Output direction programs VDD_IO/push-pull mode and then writes the requested level through `DA9055_REG_GPIO_MODE0_2`. Get reads GPIO direction, then reads either status or output-mode register before returning the target bit.

State and persistence behavior: all state persists in PMIC registers. The driver has no cache, locking, IRQ state, or suspend/resume implementation. It is a can-sleep controller.

Dependencies and integration points: depends on DA9055 MFD core, register definitions, platform data, regmap IRQ data, and platform driver registration through `subsys_initcall()`.

Risks: only three lines are exposed. Unexpected direction encoding falls through to returning a bit from the last read register, so invalid hardware state may not be clearly reported. Legacy fixed base can collide with other controllers.

Test signals: direction field programming for all three pins, output write/readback, input status reads, IRQ virq mapping from `DA9055_IRQ_GPI0`, and early registration ordering for MFD consumers.
