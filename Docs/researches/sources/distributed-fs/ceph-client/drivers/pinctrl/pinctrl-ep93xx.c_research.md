# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-ep93xx.c

## Purpose
This auxiliary driver implements a group-only pinmux controller for Cirrus EP93xx SoC variants. It exposes package-specific pin lists and mux groups for EP9301/9302, EP9307, and EP9312/EP9315 models, and programs the shared Syscon `DeviceCfg` register through the EP93xx auxiliary regmap device.

## Important APIs, Types, and Functions
`struct ep93xx_pmx` stores device, pinctrl device, auxiliary regmap device, regmap, and model. `struct ep93xx_pin_group` wraps a `struct pingroup` with a `DeviceCfg` mask/value pair. Static pin tables describe package pins for the three models. Group arrays use `PMX_GROUP` to map named groups to pin arrays and bit programming. Pinctrl callbacks are model-switching group count/name/pin accessors. Pinmux callbacks use `ep93xx_pmx_functions` and `ep93xx_pmx_set_mux`. Probe is `ep93xx_pmx_probe`; registration uses `module_auxiliary_driver`.

## Control Flow and State
The auxiliary ID selects the EP93xx model. Probe allocates state, stores the parent regmap and update callback, switches the global pinctrl descriptor to the matching pin table and pin count, sets the child firmware node to the parent node for pinctrl lookup, and registers pinctrl. Setting mux chooses the model-specific group entry, writes the group's mask/value to `EP93XX_SYSCON_DEVCFG` using the auxiliary locked update function, then reads back the register and compares changed pad bits against the expected result. Any mismatch is logged as a probable hardware limitation and returns `-EINVAL`.

## State and Persistence Behavior
Persistent state is the shared EP93xx `DeviceCfg` register. The driver itself stores only model selection and pointers. Because `ep93xx_pmx_desc` is a static global mutated at probe with model-specific pins/npins, it assumes only one compatible auxiliary instance or no conflicting concurrent probes. Register updates are serialized by the auxiliary device's `update_bits` helper and lock, not by this driver.

## Dependencies and Integration Points
The driver integrates with the EP93xx SoC auxiliary-device framework (`soc_ep93xx.pinctrl-*` IDs), `struct ep93xx_regmap_adev`, syscon/regmap, pinctrl, pinmux, generic DT mapping, and pinctrl utils. It provides mux functions such as spi, ac97, i2s, pwm, keypad, pata, lcd, and gpio depending on group support.

## Risks
Large static package pin tables and model-specific group masks are easy to desynchronize from hardware docs. The static mutable descriptor can be unsafe if multiple model instances exist. Some group definitions in the EP9307 section reference `ac97_ep9301_pins` for `i2s_on_ac97`, which deserves scrutiny. Hardware may reject writes to some DeviceCfg bits; the readback check catches this but means mux requests can fail at runtime.

## Test Signals
Validation should cover auxiliary probe for each model ID, pin count and group enumeration per model, every function-to-group mapping, successful and failing `DeviceCfg` readback verification, parent firmware-node matching for DT pinctrl states, and board boot tests for SPI/AC97/I2S/PWM/keypad/PATA/LCD/GPIO muxes.
