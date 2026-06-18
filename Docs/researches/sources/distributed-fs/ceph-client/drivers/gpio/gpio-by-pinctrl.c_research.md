
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-by-pinctrl.c

Purpose: provides a GPIO controller backed entirely by pinctrl/pinconf operations, intended for platforms such as SCMI pinctrl where pin configuration is the GPIO transport.

Important APIs/types/functions: the driver builds a bare `struct gpio_chip` in `pin_control_gpio_probe()`. GPIO callbacks are `pin_control_gpio_get_direction()`, `pinctrl_gpio_direction_input`, `pin_control_gpio_direction_output()`, `pin_control_gpio_get()`, `pin_control_gpio_set()`, and generic request/free/config helpers.

Control flow: probe allocates a gpiochip, sets label/parent/base, hooks GPIO callbacks to pinctrl helper calls, reads `ngpios` from device properties, and registers with `devm_gpiochip_add_data()`. Reads query `PIN_CONFIG_LEVEL`; writes pack `PIN_CONFIG_LEVEL` with the requested value. Direction query reads `PIN_CONFIG_OUTPUT_ENABLE`; output direction delegates to pinctrl's direction-output operation.

State and persistence behavior: the driver holds no private state beyond the gpiochip. All line state persists in the pinctrl provider or underlying firmware. There is no IRQ, suspend, cache, or reset state.

Dependencies and integration points: depends on gpiolib, internal `gpiolib.h` generic helpers, platform bus, device properties, and pinctrl consumer APIs. It matches `scmi-pinctrl-gpio`.

Risks: correctness is entirely dependent on the pinctrl provider supporting `pinctrl_gpio_get_config()` and `pinctrl_gpio_set_config()` for level and output-enable semantics. There is no local validation of `ngpios` beyond property parsing. Latency and error propagation are whatever the pinctrl provider implements.

Test signals: probe must fail cleanly without `ngpios`. GPIO get/set/direction tests should be run against a pinctrl provider that can report `PIN_CONFIG_LEVEL` and `PIN_CONFIG_OUTPUT_ENABLE`, including negative-provider-error propagation.
