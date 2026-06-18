# sources/distributed-fs/ceph-client/drivers/gpio/gpio-adp5520.c

## Purpose
This platform driver exposes the GPIO pins of the Analog Devices ADP5520 MFD PMIC. It maps enabled PMIC pins from platform data into a compact GPIO chip.

## Important APIs, types, and functions
`struct adp5520_gpio` stores the parent MFD device, `gpio_chip`, a logical-to-register-bit lookup table, and an `output` bitmap. Callbacks are `adp5520_gpio_get_value()`, `adp5520_gpio_set_value()`, `adp5520_gpio_direction_input()`, and `adp5520_gpio_direction_output()`. Probe consumes `struct adp5520_gpio_platform_data` and MFD helpers `adp5520_read()`, `adp5520_set_bits()`, and `adp5520_clr_bits()`.

## Control flow
Probe requires platform data and `pdev->id == ID_ADP5520`, builds the LUT from `gpio_en_mask`, initializes the GPIO chip, disables alternate GPIO config bits, enables C3/R3 GPIO modes when needed, applies pullups, and registers the chip. Get reads either GPIO_OUT or GPIO_IN depending on cached direction.

## State and persistence behavior
The driver stores logical output direction in `output`; PMIC registers store output values, direction bits, GPIO/LED mux mode, and pullups. Runtime changes persist in PMIC registers until changed by another PMIC consumer or reset.

## Dependencies and integration points
It depends on the ADP5520 MFD core, legacy platform data, and gpiolib. The GPIO chip uses the platform-supplied base when provided and can sleep because parent MFD register access may sleep.

## Risks and edge cases
The driver is platform-data only and rejects non-ADP5520 IDs. It uses bitwise OR accumulation for multi-step register writes, so the first failing MFD operation must still be noticed. The `output` bitmap is local state and may become stale if another function changes direction outside this driver.

## Test signals
Useful tests cover missing platform data, zero enabled GPIOs, C3/R3 mode setup, pullup mask writes, input versus output reads using the proper register, and correct logical line mapping through `lut[]`.
