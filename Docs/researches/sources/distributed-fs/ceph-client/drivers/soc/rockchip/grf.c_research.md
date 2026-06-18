# sources/distributed-fs/ceph-client/drivers/soc/rockchip/grf.c

## Purpose

`grf.c` applies early default settings to Rockchip General Register Files. It disables problematic JTAG switching, selects PWM/clock behavior, configures weak pulls, and applies USB3 OTG quirks for selected SoCs.

## Important APIs, Types, and Functions

`struct rockchip_grf_value` describes one register write with a description, offset, and hiword-mask value. `struct rockchip_grf_info` groups arrays per compatible. Static data covers RK3036, RK3128, RK3228, RK3288, RK3328, RK3368, RK3399, RK3566, RK3576, and RK3588 GRF variants. `rockchip_grf_init()` iterates matching DT nodes, gets their syscon regmap, and writes all values.

## Control Flow

`postcore_initcall()` runs after core init. For each available matching node, it resolves the syscon regmap and writes each default value, logging failures but continuing through the array. Fatal errors occur for missing match data or unavailable syscon regmap.

## State and Persistence Behavior

The driver keeps no runtime state. It mutates GRF hardware registers early; those settings persist until reset or later writes.

## Dependencies and Integration Points

It depends on OF matching, syscon/regmap, and `FIELD_PREP_WM16_CONST()` hiword-mask semantics. It integrates with pinctrl, MMC, USB, PWM, I3C, and clock expectations by applying safe defaults.

## Risks and Edge Cases

Wrong GRF defaults can break board pinmux or peripheral routing globally. Because writes are early and unconditional for available nodes, board-specific exceptions are hard to express. Errors in individual writes are logged but do not abort, so partially applied defaults are possible.

## Test Signals

Boot each compatible SoC, read back GRF fields where readable, validate MMC/JTAG/PWM/USB/I3C behavior, and test unavailable syscon failure paths. Static checks should verify hiword-mask values target correct bits.
