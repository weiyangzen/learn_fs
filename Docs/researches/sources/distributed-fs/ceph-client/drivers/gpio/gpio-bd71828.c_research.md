# sources/distributed-fs/ceph-client/drivers/gpio/gpio-bd71828.c

## Purpose
This platform driver exposes four BD71828 PMIC GPIO-related pins, including a special HALL input pin. Most pins are treated as output-only because their OTP-selected roles cannot be read at runtime.

## Important APIs, types, and functions
`struct bd71828_gpio` stores regmap, device, and gpiochip. Operations are `bd71828_gpio_set()`, `bd71828_gpio_get()`, `bd71828_gpio_set_config()`, and `bd71828_get_direction()`. `GPIO_OUT_REG(off)` maps logical pins to consecutive GPIO control registers, and `HALL_GPIO_OFFSET` identifies the input-only pin.

## Control flow
Probe allocates state, initializes a 4-line sleeping gpiochip with parent MFD device and callbacks, obtains the parent regmap, and registers. Set/config are no-ops or unsupported for the HALL input; other pins update output and drive bits.

## State and persistence behavior
Pin output and drive state live in PMIC GPIO control registers. HALL input state is read from `BD71828_REG_IO_STAT`. Direction is inferred from fixed pin semantics and board-reserved ranges, not dynamic hardware state.

## Dependencies and integration points
The driver depends on the BD71828 MFD regmap, platform device binding `bd71828-gpio`, gpiolib, and pinconf drive config. Board firmware is expected to use `gpio-reserved-ranges` for pins not configured by OTP as GPIO outputs.

## Risks and edge cases
OTP pin usage cannot be verified at runtime, so incorrect device-tree exposure can let software drive pins with non-GPIO board functions. `get()` returns the masked register field rather than normalized boolean for non-HALL pins, so callers get nonzero truth but not necessarily `1`.

## Test signals
Test HALL input reads and output rejection, output pins set/get, drive mode pinconf, regmap absence failure, and board reserved-range behavior in gpiolib.
