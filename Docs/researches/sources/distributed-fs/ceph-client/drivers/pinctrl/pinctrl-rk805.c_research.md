# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-rk805.c

## Purpose
This driver exposes the GPIO-capable pins on Rockchip RK805, RK806, and RK816 PMICs as both a `gpio_chip` and a pinctrl provider. It is a child platform driver of the RK808-family MFD device and uses the parent PMIC regmap to switch pin mux functions, read/write GPIO values, and control direction where the PMIC variant supports it. The hardware surface is small: RK805 has two output-only GPIOs, RK806 has three sleep/power-control pins with multiple function selections, and RK816 has one pin that can be thermistor or GPIO.

## Important APIs, Types, And Functions
`struct rk805_pctrl_info` is the central state object, holding the parent `struct rk808`, device, registered `pinctrl_dev`, embedded `gpio_chip`, copied `pinctrl_desc`, and variant-selected pin/function/group/config tables. `struct rk805_pin_config` maps each logical pin to the PMIC register and masks for function, direction, and value bits. Static tables define pin descriptors, groups, and functions for RK805/RK806/RK816.

Gpiolib callbacks are `rk805_gpio_get()`, `rk805_gpio_set()`, `rk805_gpio_direction_output()`, and `rk805_gpio_get_direction()`. Pinctrl callbacks are the simple group/function enumerators plus `rk805_pinctrl_set_mux()`, `rk805_pinctrl_gpio_request_enable()`, and `rk805_pmx_gpio_set_direction()`. Pinconf support is limited to `PIN_CONFIG_LEVEL` and `PIN_CONFIG_INPUT_ENABLE` through `rk805_pinconf_get()` and `rk805_pinconf_set()`.

## Control Flow
Probe attaches the child device firmware node to the parent MFD node, allocates state, copies the template gpio and pinctrl descriptors, then switches on `rk808->variant` to select the correct pin tables and `pin_cfg` array. It registers the GPIO chip first, then the pinctrl device, and finally adds a one-to-one GPIO pin range.

GPIO reads and writes are direct `regmap_read()` and `regmap_update_bits()` operations against the parent PMIC. Direction output sets the requested value first, then asks pinctrl to program output mode. GPIO request-enable selects the GPIO mux value for RK805 and RK816, but uses RK806 function 5 as the GPIO function. Pinconf level configuration similarly writes the value and forces output direction, while input-enable is accepted only for non-RK805 variants with a nonzero argument.

## State And Persistence
The driver has no persistent storage and no PM callbacks of its own. Software state is the variant-selected static table set plus gpiolib/pinctrl registration state. Pin value, mux, and direction persist in PMIC registers until changed by firmware, reset, suspend policy, or another PMIC user. RK805 pins intentionally behave as output-only because their `dir_msk` and `fun_msk` fields are absent.

## Dependencies And Integration Points
It depends on the RK808 MFD core for `struct rk808`, variant IDs, register definitions, and the regmap. It integrates with platform-device child creation from the MFD, gpiolib, pinctrl, pinmux, generic pinconf DT parsing via `pinconf_generic_dt_node_to_map_pin()`, and `gpiochip_add_pin_range()`. Device-tree consumers see the parent PMIC firmware node rather than a separate child node because probe calls `device_set_node()`.

## Risks And Test Signals
Risk is concentrated in variant-specific masks: a wrong `fun_msk`, `dir_msk`, or `val_msk` writes PMIC power/sleep control bits rather than ordinary GPIO state. `_rk805_pinctrl_set_mux()` logs regmap failures but returns 0, so mux write failures can be hidden from pinctrl consumers. RK805 input-enable is intentionally unsupported, and RK806 GPIO selection depends on function 5 rather than a function named `gpio`. Test signals include successful probe for all three variants, correct gpio count and pin names, output-only behavior on RK805, RK816 thermistor/GPIO mux switching, RK806 function selection across all three pins, pinconf `level` writes, input-enable rejection/acceptance by variant, and regmap error injection for value/direction paths.
