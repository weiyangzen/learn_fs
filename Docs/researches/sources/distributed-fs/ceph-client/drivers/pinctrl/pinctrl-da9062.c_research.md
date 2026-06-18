# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-da9062.c

## Purpose
This platform driver exposes the five DA9062 PMIC GPIO pins through gpiolib and limited generic pin configuration. Despite the filename and description mentioning pinctrl, the current implementation registers only a gpiochip; pinmux/pinctrl alternate-mode support is left as a TODO.

## Important APIs, Types, and Functions
`struct da9062_pctl` stores the parent `struct da9062`, a gpiochip, and desired output pin modes in `pin_config`. Mode helpers are `da9062_pctl_get_pin_mode` and `da9062_pctl_set_pin_mode`. GPIO callbacks are `da9062_gpio_get`, `da9062_gpio_set`, `da9062_gpio_get_direction`, `da9062_gpio_direction_input`, `da9062_gpio_direction_output`, `da9062_gpio_set_config`, and `da9062_gpio_to_irq`. Probe is `da9062_pctl_probe`.

## Control Flow and State
Probe sets the child device firmware node to the parent, allocates state, gets parent drvdata, exits successfully without registering GPIO when the parent lacks `gpio-controller`, initializes all desired output modes to push-pull, copies a template gpiochip, fills label and parent, stores drvdata, and registers the gpiochip. Direction input writes GPI mode and programs active-high/active-low type bits according to the gpiod descriptor. Direction output restores the saved output mode from `pin_config` and then writes the output level. Set-config validates PMIC restrictions: pull-down only in input mode and pull-up only in open-drain output mode.

## State and Persistence Behavior
Hardware state lives in DA9062 regmap registers for GPIO mode, status, output level, config, and IRQ mapping. Driver-side `pin_config[]` persists the selected output drive mode so a later direction-output operation can restore open-drain or push-pull instead of always using one mode. The gpiochip is sleeping because all operations go through PMIC regmap I/O.

## Dependencies and Integration Points
The driver depends on the DA9062 MFD parent, regmap, DA9062 register definitions, gpiolib, GPIO descriptors, property APIs, and regmap IRQ mapping. Compatible string is `dlg,da9062-gpio`; platform alias is `da9062-gpio`.

## Risks
No pinctrl device is registered, so consumers expecting pinctrl states from this file will not get them. `da9062_gpio_set` shifts raw `value` into the bit position without boolean normalization, so callers should pass normal 0/1 values as gpiolib does. Bias configuration depends on current mode and can return `-ENOTSUPP` when called in the wrong order. Alternate mode returns `-ENOTSUPP` for get/direction.

## Test Signals
Tests should cover probe with and without parent `gpio-controller`, input and output direction transitions, open-drain/push-pull set_config persistence through direction_output, active-low input type programming, GPIO get from status versus output registers, and `to_irq` mapping for all five GPI IRQs.
