<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-madera.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-madera.c

## Purpose
`gpio-madera.c` exposes GPIOs on Cirrus Logic Madera codec MFD devices and registers an explicit fixed pin range to the Madera pinctrl driver.

## Important APIs, types, and functions
`struct madera_gpio` stores the parent `struct madera` and gpiochip. GPIO callbacks use per-pin register pairs at `MADERA_GPIO1_CTRL_1/2 + 2 * offset` for level and direction. Probe selects `ngpio` based on codec type and calls `gpiochip_add_pin_range()`.

## Control flow
Probe obtains parent MFD state and pdata, copies a gpiochip template, sets parent and base, switches on codec type for line count, registers the chip, then maps all GPIOs to the `madera-pinctrl` pinctrl range. Direction output clears the direction bit first and then sets the level bit.

## State and persistence behavior
GPIO state is in codec regmap registers. Platform data can preserve a legacy fixed gpio base; otherwise dynamic numbering is used. No software shadow is kept.

## Dependencies and integration points
It is a platform child `madera-gpio`, depends on Madera MFD register definitions, regmap, pdata, and the `pinctrl-madera` driver, declared with a soft dependency.

## Risks and edge cases
Unknown codec variants fail probe. Pin range registration failure aborts after gpiochip registration through devm cleanup. The driver assumes fixed silicon mapping between GPIOs and pinctrl pins.

## Test signals
Test each Madera variant line count, fixed and dynamic bases, direction/value register updates, generic pinconf routing to pinctrl, pin range registration, and load ordering with pinctrl-madera.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-madera.c -->
