# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-axp209.c

## Purpose
This platform driver exposes GPIO and pinmux support for X-Powers AXP20x PMIC families, including AXP209, AXP221/22x, and AXP813 variants. It maps PMIC GPIO pins to pinctrl groups and gpiolib lines and supports GPIO input/output, LDO mux membership, and ADC muxing where the specific chip descriptor allows it.

## Important APIs, Types, and Functions
`struct axp20x_pctrl_desc` describes per-chip pins, pin count, LDO-capable mask, ADC-capable mask, GPIO status bit offset, and ADC mux value. `struct axp20x_pctl` stores gpiochip, regmap, pinctrl device, device, descriptor, and four function descriptors. Key helpers include `axp20x_gpio_get_reg`, `axp20x_gpio_get`, `axp20x_gpio_get_direction`, `axp20x_gpio_set`, `axp20x_pmx_set`, `axp20x_pmx_set_mux`, `axp20x_pmx_gpio_set_direction`, `axp20x_funcs_groups_from_mask`, and `axp20x_build_funcs_groups`. Probe is `axp20x_pctl_probe`.

## Control Flow and State
Probe first checks DT availability and retrieves parent `struct axp20x_dev` drvdata. It allocates `struct axp20x_pctl`, initializes the gpiochip callbacks, selects the chip descriptor via OF match data, attaches the parent PMIC regmap, stores drvdata, builds function-to-group lists, allocates a pinctrl descriptor, registers pinctrl, registers the gpiochip, and adds a pin range. GPIO direction and mux paths write PMIC control registers via regmap. GPIO3 on AXP209 uses a special control layout and is handled separately for value, direction, and mux programming.

## State and Persistence Behavior
The driver owns no cache; persistent state is in PMIC registers accessed through the parent MFD regmap. Function membership is generated at probe and stored in devm-managed arrays. LDO mux selection deliberately returns success without writing bits because those mux bits overlap regulator on/off control and are left to the regulator framework. GPIO output path uses `chip->set`, while direction changes from gpiolib go through pinctrl GPIO direction helpers.

## Dependencies and Integration Points
The driver depends on the AXP20x MFD parent (`struct axp20x_dev`), regmap, OF match data, pinctrl, pinmux, pinconf DT map helpers, and gpiolib. Compatible strings are `x-powers,axp209-gpio`, `x-powers,axp221-gpio`, and `x-powers,axp813-gpio`.

## Risks
AXP209 GPIO3 has a different bit layout, making it a likely source of regressions. `axp20x_group_pins` casts a pin descriptor address to `unsigned int *`, so pinctrl core expectations should be watched carefully. LDO mux intentionally does not program hardware; tests must distinguish this from a missing implementation. ADC support varies by descriptor mask and mux value. The probe info message always says "AXP209" even when matching AXP22x/AXP813.

## Test Signals
Expected test signals include PMIC child-device probe through MFD, pinctrl function enumeration for gpio_out/gpio_in/ldo/adc, GPIO read/write and direction for normal pins and GPIO3, pin range registration, rejection of ADC/LDO functions on unsupported pins, and no regulator state changes when selecting LDO mux.
