
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-da9052.c

Purpose: exposes the 16 GPIO pins of Dialog DA9052 PMICs through the DA9052 MFD register API and regmap IRQ framework.

Important APIs/types/functions: `struct da9052_gpio` stores the parent `struct da9052` and gpiochip. Callbacks are `da9052_gpio_get()`, `da9052_gpio_set()`, `da9052_gpio_direction_input()`, `da9052_gpio_direction_output()`, and `da9052_gpio_to_irq()`. `reference_gp` is the template gpiochip copied in probe.

Control flow: probe gets parent MFD state and optional platform data, copies `reference_gp`, applies a legacy base if supplied, and registers the gpiochip. Get first reads the GPIO configuration nibble to determine input or push-pull output; input reads `STATUS_C` or `STATUS_D`, while output reads the mode bit from the GPIO config register. Direction functions update the correct lower or upper nibble in paired GPIO config registers. IRQ mapping offsets from `DA9052_IRQ_GPI0`.

State and persistence behavior: PMIC registers hold direction, output level, debounce, and active polarity. The driver has no shadow cache or PM state. Operations sleep through the MFD/regmap transport and `can_sleep` is set.

Dependencies and integration points: depends on DA9052 MFD core, DA9052 register definitions/platform data, regmap IRQ data, platform children, and gpiolib.

Risks: `get()` only handles input and push-pull output; open-drain or unexpected modes return `-EINVAL`. Legacy `gpio_base` support can conflict with dynamic GPIO numbering. Direction input hardcodes active-low with debounce enabled.

Test signals: nibble updates for odd/even pins, input status reads across both status registers, push-pull output readback, IRQ mapping for all 16 lines, and platform-data base handling.
