# sources/distributed-fs/ceph-client/drivers/leds/leds-88pm860x.c

## Purpose
Implements LED support for Marvell 88PM860x MFD PMIC RGB outputs. Each platform child device represents one color channel and registers a basic LED class device that programs PMIC PWM/current/blink control registers.

## Important APIs, Types, And Functions
`struct pm860x_led` contains the LED classdev, PMIC I2C client, parent chip, per-LED mutex, name, port, current setting, cached brightness, control/blink registers, and blink enable mask. Main callbacks are `pm860x_led_set`, `led_power_set`, `pm860x_led_dt_init`, `pm860x_led_probe`, and `pm860x_led_remove`.

## Control Flow
Probe obtains `control` and `blink` register resources, maps platform ID 0-5 to names `led0-red/green/blue` or `led1-red/green/blue`, selects the proper PMIC I2C client, reads optional DT current setting from the parent `leds` node or platform data, initializes the classdev, registers it, and turns it off.

Brightness writes compress LED brightness to a five-bit PWM value. Transitioning from off to on enables the oscillator group, programs current if configured, sets continuous-on blink timing, and enables the group blink bit. Transitioning to zero writes the PWM and then bulk-reads sibling control registers; if all three channel PWM values are zero it clears current and blink enable and disables the oscillator.

## State And Persistence
Per-LED cached `brightness` and `current_brightness` are protected by `lock`. Hardware state persists in PM860x PMIC registers and oscillator enables shared by RGB groups.

## Dependencies And Integration Points
Depends on the 88PM860x MFD API, platform resources, I2C register helpers, optional OF child lookup, and the LED class. Platform alias is `88pm860x-led`.

## Risks
Group power control is shared across three color channels and relies on bulk-reading adjacent registers to decide when all are off. Platform IDs must match MFD resource layout. Error returns from several PMIC writes are not all propagated in detail, so partial hardware programming can be hard to diagnose.

## Test Signals
Test each of six platform IDs, verify names and current settings, toggle individual colors, ensure oscillator remains enabled while any sibling color is active and disables when all are off, and validate remove unregisters the classdev cleanly.
