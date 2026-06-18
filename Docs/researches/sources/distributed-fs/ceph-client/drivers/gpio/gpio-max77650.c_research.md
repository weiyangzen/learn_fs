<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-max77650.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-max77650.c

## Purpose
`gpio-max77650.c` exposes the single GPIO/GPI pin on MAX77650/MAX77651 charger/power-supply MFD devices.

## Important APIs, types, and functions
`struct max77650_gpio_chip` stores the parent regmap, gpiochip, and GPI IRQ number. GPIO callbacks implement direction input/output, set/get, get_direction, pinconf drive/debounce, and `max77650_gpio_to_irq()`.

## Control flow
Probe gets the parent I2C device and regmap, obtains the named `GPI` IRQ, initializes a one-line can-sleep gpiochip with dynamic base and the parent I2C name as label, and registers it. Direction output updates direction and output bits together; get reads input-value bits; `to_irq` returns the pre-fetched parent IRQ.

## State and persistence behavior
All state lives in `MAX77650_REG_CNFG_GPIO`. The driver keeps only the IRQ number. Debounce config is a single enable bit, not a duration.

## Dependencies and integration points
It is a platform child `max77650-gpio`, depends on MAX77650 MFD regmap and named IRQ resource `GPI`, and exposes pinconf open-drain/push-pull and debounce.

## Risks and edge cases
`get_direction()` returns the raw direction bit values, relying on gpiolib's convention that input is nonzero. `set_config(PIN_CONFIG_INPUT_DEBOUNCE)` ignores the requested debounce argument and simply enables debounce. Only one GPIO exists, so consumers must not expect per-offset IRQ variation.

## Test signals
Test one-line get/set/direction, `to_irq` mapping to named GPI IRQ, drive mode config, debounce enable behavior, and missing regmap or IRQ probe failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-max77650.c -->
