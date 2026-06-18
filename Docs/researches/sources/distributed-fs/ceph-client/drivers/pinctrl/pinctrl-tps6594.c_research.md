# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-tps6594.c

## Purpose
`pinctrl-tps6594.c` is the pinmux and GPIO-regmap driver for TI TPS6594-family PMICs, including TPS6593, TPS6594, LP8764, TPS65224, and TPS652G1 variants. It exposes PMIC GPIO pins as pinctrl groups, maps named alternate functions to GPIO configuration register mux values, and registers GPIO access through `gpio-regmap`.

## Important APIs, Types, and Functions
Function tables are built from `struct tps6594_pinctrl_function`, which combines a `struct pinfunction` with a mux value. Variant templates (`tps6594_template_pinctrl`, `tps65224_template_pinctrl`, `tps652g1_template_pinctrl`) select pins, functions, mux mask, remap table, and counts. `struct muxval_remap` handles pins whose mux value differs from the common function value. `struct tps6594_pinctrl` stores the parent MFD pointer, gpio-regmap device, pinctrl device, selected tables, mux mask, and remap metadata.

Pinctrl callbacks enumerate one group per pin and use `pinconf_generic_dt_node_to_map_group()` for DT maps. Pinmux callbacks enumerate functions, return legal groups from the static pinfunction definitions, set muxes with `tps6594_pmx_set_mux()`, and force GPIO muxing from `tps6594_pmx_gpio_set_direction()`. GPIO register translation is handled by `tps6594_gpio_regmap_xlate()`.

## Control Flow
Probe obtains the parent `struct tps6594`, allocates a pinctrl descriptor and state, switches on `tps->chip_id`, copies the relevant template, fills `gpio_regmap_config`, registers pinctrl, then registers gpio-regmap. The mux path gets the selected function's default mux value, applies any group-specific remap, and writes the mux select bits in `TPS6594_REG_GPIOX_CONF(pin)` with `regmap_update_bits()`. GPIO-regmap translates direction, input, and output base registers into the correct PMIC register and bit mask; GPIO direction output uses the direction bit in each GPIO configuration register.

## State and Persistence
State is entirely in the PMIC regmap registers plus static per-variant tables copied at probe. There is no local locking in this file; regmap and gpio-regmap provide the access serialization. There is no suspend/resume handling here, so persistence depends on PMIC retention and parent MFD/regmap behavior. No pinconf operations are implemented beyond group DT mapping; this file is mux and GPIO only.

## Dependencies and Integration Points
The driver depends on the TPS6594 MFD core for chip ID, register definitions, and regmap; pinctrl/pinmux core; generic pinconf group DT map helpers; platform device matching from the MFD; and `gpio-regmap` for GPIO operations. Consumers select named functions such as `nsleep1`, `wkup`, `clk32kout`, `scl_i2c2_cs_spi`, or variant-specific names on named groups `GPIO0`...`GPIO10` or `GPIO0`...`GPIO5`.

## Risks
The default switch case in probe leaves the descriptor and template largely empty but still proceeds, so an unsupported `chip_id` from the parent could register a broken zero-pin controller instead of failing. Remap tables are essential for special pins; missing entries silently write the common mux value. `tps6594_pmx_gpio_set_direction()` ignores the `input` argument and only selects GPIO mux, leaving actual direction to gpio-regmap. No explicit IRQ or pinconf support is provided here, so expectations must be met by other PMIC blocks or not advertised. Static template structs are copied then patched with `tps`, which is fine, but future mutable fields should avoid sharing through template pointers.

## Test Signals
Test probe for every supported chip ID, group/function enumeration counts, DT mux selection for every function's legal group list, remapped mux values on TPS6594 GPIO8/GPIO9 and TPS65224 GPIO5, GPIO input/output register translation across one-register and two-register layouts, unsupported chip ID behavior, and regmap error propagation from mux writes and gpio-regmap registration.
