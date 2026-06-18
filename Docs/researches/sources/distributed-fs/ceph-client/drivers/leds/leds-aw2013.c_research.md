# sources/distributed-fs/ceph-client/drivers/leds/leds-aw2013.c

## Purpose
Implements the Awinic AW2013 three-channel I2C LED driver with regulator-managed power, brightness, and hardware blink timing.

## Important APIs, Types, And Functions
`struct aw2013` stores mutex, two regulators, client, LED array, regmap, LED count, and enabled flag. `struct aw2013_led` stores chip pointer, classdev, channel number, and maximum current setting. Important functions are `aw2013_chip_init/enable/disable/in_use`, `aw2013_brightness_set`, `aw2013_blink_set`, `aw2013_probe_dt`, and `aw2013_probe`.

## Control Flow
Probe initializes mutex, regmap, regulators, powers the chip, reads the reset/ID register, installs a devm disable action, parses child nodes, registers LEDs, then disables regulators to save power. Child parsing resets the chip, reads channel `reg`, optional `led-max-microamp`, computes IMAX, assigns blocking brightness and blink callbacks, and registers each classdev.

Brightness enables regulators/chip when any LED should be active, writes PWM, toggles channel enable, disables blink mode when turning off, and powers the chip down when all cached classdev brightness values are zero. Blink defaults unspecified requests to 500/500, ensures LED brightness is nonzero, converts on/off delays to hardware powers-of-two in 130 ms units, writes timing registers, enables mode and channel bits.

## State And Persistence
Software state tracks `enabled`, LED count, per-classdev brightness, and per-channel IMAX. Hardware state is lost when regulators are disabled and reinitialized by `aw2013_chip_enable`. Mutex protects register writes and power transitions.

## Dependencies And Integration Points
Depends on I2C, regmap, two regulators (`vcc`, `vio`), OF child nodes, and LED class. Compatible string is `awinic,aw2013`.

## Risks
`aw2013_brightness_set` checks `aw2013_chip_in_use` before the LED core updates the target `cdev.brightness`, so power-up decisions depend on current cached state and deserve regression tests. Blink delay conversion uses `ilog2((*delay - 1) / 130) + 1`; very small nonzero delays need careful validation. Power cycling means all state must be restored by `aw2013_chip_init` and subsequent writes.

## Test Signals
Probe should validate chip ID, parse up to three LEDs, compute IMAX, power down when idle, and power up on brightness/blink. Test blink default and quantized delay return values, off transitions clearing mode bits, and regulator cleanup on probe failure/remove.
