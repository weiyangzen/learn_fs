# sources/distributed-fs/ceph-client/drivers/gpio/gpio-altera-a10sr.c

## Purpose
This platform driver exposes GPIO lines on the Altera Arria10 MAX5 System Resource Chip through the parent MFD regmap. It represents LED/output and pushbutton/DIP-switch input functions as one 12-line GPIO chip.

## Important APIs, types, and functions
`struct altr_a10sr_gpio` stores a `gpio_chip` and parent regmap. Callbacks are `altr_a10sr_gpio_get()`, `altr_a10sr_gpio_set()`, `altr_a10sr_gpio_direction_input()`, and `altr_a10sr_gpio_direction_output()`. Probe clones `altr_a10sr_gc`, sets parent/fwnode, and registers with `devm_gpiochip_add_data()`.

## Control flow
Probe obtains the parent `struct altr_a10sr`, stores its regmap, copies the static chip template, and registers the chip. Input direction is accepted only for offsets in the input-valid range; output direction is accepted only for offsets in the output-valid range and writes the initial value.

## State and persistence behavior
GPIO state lives in the parent chip registers: reads use `ALTR_A10SR_PBDSW_REG`, writes update `ALTR_A10SR_LED_REG`. The driver stores no cache and relies on regmap for access serialization.

## Dependencies and integration points
The driver depends on the `altera-a10sr` MFD core, regmap, gpiolib, and OF compatible `altr,a10sr-gpio`. It uses the platform device fwnode for GPIO firmware bindings while setting the chip parent to the MFD parent.

## Risks and edge cases
Offset arithmetic is tied to `ALTR_A10SR_LED_VALID_SHIFT` and valid-range constants. The `get` path uses `BIT(offset - shift)`, so invalid output offsets should be filtered by direction/consumer usage to avoid nonsensical bit positions. The chip is sleeping because parent register access may sleep.

## Test signals
Check `ngpio == 12`, valid input/output range enforcement, LED register updates for outputs, pushbutton/DIP reads for inputs, and probe through an Arria10 system-resource MFD child node.
