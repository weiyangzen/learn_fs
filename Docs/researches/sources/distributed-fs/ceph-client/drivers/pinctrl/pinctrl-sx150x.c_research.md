# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-sx150x.c

## Purpose
`pinctrl-sx150x.c` supports Semtech SX1501-SX1509 I2C GPIO expanders as combined pinctrl, GPIO, pinconf, and optional IRQ controllers. It hides multiple chip register layouts behind a custom regmap and supports 4, 8, and 16 GPIO variants plus the oscillator output pin on SX1507/8/9 devices.

## Important APIs, Types, and Functions
`struct sx150x_device_data` describes each chip model's register offsets, GPIO count, pin descriptors, and model-specific private registers. `struct sx150x_pinctrl` owns the I2C client, regmap, pinctrl device, gpiochip, IRQ cached mask/sense state, mutex, and selected device data. GPIO callbacks implement direction/data access and special OSCIO handling. Pinconf callbacks support pull-up/down, open-drain/push-pull where available, and output level. IRQ callbacks maintain cached edge sense and mask values and dispatch nested interrupts from the IRQ source register.

The custom regmap is the most important abstraction. `sx150x_regmap_reg_width()`, `sx150x_maybe_swizzle()`, `sx150x_regmap_reg_read()`, and `sx150x_regmap_reg_write()` make one logical 32-bit regmap value represent one or more SMBus bytes, including two-bit-per-line `RegSense` and byte-swizzled 16-pin SX1503/SX1506 layouts.

## Control Flow
`sx150x_probe()` checks SMBus functionality, selects OF/I2C match data, initializes the custom cached regmap, initializes hardware, registers pinctrl, configures and registers the gpiochip, optionally configures nested threaded IRQ support if `client->irq` is present, enables pinctrl after gpiochip registration, and adds a pin range. Hardware initialization optionally resets SX1507/8/9 when `semtech,probe-reset` is present, programs miscellaneous/autoclear behavior, and sets pins to normal mode by clearing polarity or PLD mode.

GPIO direction and data access write the logical direction/data registers through regmap. IRQ set-type rejects level IRQs and encodes rising/falling bits into the cached `sense` field; bus sync writes mask and sense registers. The IRQ thread reads and acknowledges the source register, then calls nested IRQ handlers for each active GPIO.

## State and Persistence
The persistent hardware state includes direction, data, pull, drain, polarity/PLD, IRQ mask/source/sense, and oscillator clock registers. Runtime-only cached state includes `pctl->irq.masked` and `pctl->irq.sense`, protected by `pctl->lock` in irq bus lock/unlock. Regmap uses `REGCACHE_MAPLE`, with IRQ source and data marked volatile. There is no suspend/resume path in this file, so restore behavior depends on regmap cache and parent I2C/device power behavior outside this driver.

## Dependencies and Integration Points
The driver integrates with I2C/SMBus byte data, regmap custom bus callbacks, OF/I2C device matching, pinctrl generic per-pin config DT helpers, gpiochip generic config, nested threaded GPIO IRQ support, and subsystem init ordering via `subsys_initcall`. Device tree compatibles choose exact register maps and whether OSCIO is exposed as an extra pin.

## Risks
The source comments state that 4-bit chips are untested. The custom regmap is layout-sensitive; any wrong width or swizzle corrupts multi-byte registers. `sx150x_pinconf_get()` appears to test `if (!ret)` after masking `data` for pull-up/down cases, but `ret` is the successful return code rather than the masked data value; that path likely fails to reject disabled pulls as intended. `sx150x_gpio_set_multiple()` is disabled for SX150X_789 because OSCIO lives in a separate register, but other multi-register edge cases depend on the logical regmap width being correct. IRQ handling supports edge-only IRQs and acknowledges by writing the source value; parent polarity is hard-coded as falling for the requested threaded IRQ.

## Test Signals
Test every compatible's register width calculation, especially SX1503/SX1506 `RegSense` swizzling, GPIO direction/data over 4/8/16-bit devices, OSCIO level behavior, pull-up/down and drain pinconf, optional probe reset, IRQ mask/type/source acknowledgment, and pin range registration. Regression tests should include pull get semantics when the pull bit is disabled, absent IRQ operation, and I2C error propagation from custom regmap reads/writes.
