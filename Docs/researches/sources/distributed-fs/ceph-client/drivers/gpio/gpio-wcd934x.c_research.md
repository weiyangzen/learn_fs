# sources/distributed-fs/ceph-client/drivers/gpio/gpio-wcd934x.c

## Purpose
Adds gpiolib support for the five GPIO pins in Qualcomm WCD9340/WCD9341 audio codec MFDs using the parent regmap.

## Important APIs, Types, And Functions
- `struct wcd_gpio_data` holds the parent `regmap` and embedded `gpio_chip`.
- `wcd_gpio_get_direction`, `wcd_gpio_direction_input`, `wcd_gpio_direction_output`, `wcd_gpio_get`, and `wcd_gpio_set` manipulate direction and value bits in `WCD_REG_DIR_CTL_OFFSET` and `WCD_REG_VAL_CTL_OFFSET`.
- `wcd_gpio_probe` fetches the parent regmap, initializes a sleepable five-line chip, and registers it.

## Control Flow
Probe binds from OF compatibles, obtains the parent regmap, fills gpiolib callbacks, and registers a dynamic-base chip. Direction input clears the pin bit in the direction register. Direction output sets the direction bit first and then writes the requested value bit. Get reads the value-control register and masks the pin bit.

## State And Persistence
The driver keeps no local state beyond the chip/regmap pointer. Direction and value persist in codec registers according to parent device power/reset behavior.

## Dependencies And Integration Points
Integrates with the Qualcomm WCD934x MFD/regmap parent and the platform bus compatibles `qcom,wcd9340-gpio` and `qcom,wcd9341-gpio`. It exposes `can_sleep = true` because regmap access can sleep.

## Risks And Edge Cases
`wcd_gpio_get` ignores a regmap read error and may return a stale/undefined masked value if the read fails. Direction-output is not atomic: a failure after setting direction can leave the pin configured as output with the old value. There is no IRQ support and no pin configuration beyond direction/value.

## Test Signals
Verify parent regmap absence returns `-EINVAL`, all five pin bits map correctly, direction and value writes target the expected registers, read-error injection on get is noticed by tests, and dynamic GPIO base registration succeeds from both compatible strings.
