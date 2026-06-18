# sources/distributed-fs/ceph-client/drivers/gpio/gpio-bd9571mwv.c

## Purpose
This platform driver exposes the two GPIOs of ROHM BD9571MWV-M and BD9574MWF-M PMICs. Interrupt support is explicitly not implemented.

## Important APIs, types, and functions
`struct bd9571mwv_gpio` stores a parent regmap and gpiochip. Callbacks are `bd9571mwv_gpio_get_direction()`, `bd9571mwv_gpio_direction_input()`, `bd9571mwv_gpio_direction_output()`, `bd9571mwv_gpio_get()`, and `bd9571mwv_gpio_set()`. Probe copies a 2-line chip template and registers it.

## Control flow
Probe allocates state, gets the parent MFD regmap, sets the chip parent to the MFD device, and registers the gpiochip. Direction output writes the initial output value first, then sets the direction bit. Direction input clears the direction bit.

## State and persistence behavior
Direction, input, and output state are stored in PMIC registers `BD9571MWV_GPIO_DIR`, `BD9571MWV_GPIO_IN`, and `BD9571MWV_GPIO_OUT`. The driver holds no cache and uses regmap for all operations.

## Dependencies and integration points
It depends on ROHM generic MFD platform IDs, BD9571 register definitions, regmap, and gpiolib. Platform IDs cover both BD9571 and BD9574 variants.

## Risks and edge cases
The direction bit convention must match hardware: the code reports set bits as input but sets the bit after configuring output, which should be verified against the PMIC datasheet. Return values from direction setters ignore `regmap_update_bits()` failures, so write errors may be hidden. No IRQ support exists.

## Test signals
Test both platform IDs, parent regmap presence, direction get/set semantics against hardware, input and output reads, output value writes, and behavior under injected regmap write errors.
