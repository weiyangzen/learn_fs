# sources/distributed-fs/ceph-client/drivers/hwmon/aspeed-g6-pwm-tach.c

## Purpose
This platform driver supports the newer Aspeed AST2600/AST2700 PWM/tach controller. It registers a Linux PWM chip for 16 PWM outputs and a hwmon device for up to 16 tachometer fan inputs described by device tree child nodes.

## Important APIs, Types, And Functions
`struct aspeed_pwm_tach_data` stores MMIO base, clock/reset handles, clock rate, tach-present bitmap, and current tach divisor. PWM behavior is implemented through `aspeed_pwm_ops`, specifically `aspeed_pwm_get_state()` and `aspeed_pwm_apply()`. Tach hwmon behavior is implemented by `aspeed_tach_hwmon_read()`, `aspeed_tach_hwmon_write()`, and `aspeed_tach_dev_is_visible()`.

`aspeed_pwm_apply()` computes high/low clock divisors for a requested period, fixes the hardware period field to its maximum for duty resolution, maps 0 percent duty to clock-disable and 100 percent duty to equal rising/falling semantics, and writes control/duty registers. `aspeed_present_fan_tach()` programs debounce, edge mode, clock divisor, threshold bits, marks channels present, and enables tach channels.

## Control Flow And State
Probe maps MMIO, enables the clock, deasserts reset with a devm reset action, allocates and registers a 16-channel PWM chip, walks child nodes reading `tach-ch`, initializes each listed tach channel, registers hwmon named `aspeed_tach`, and populates child platform devices. Runtime PWM consumers use the PWM framework; fan reads use hwmon callbacks and return RPM only after `TACH_ASPEED_FULL_MEASUREMENT` is set.

State is mostly hardware register state plus in-memory `tach_present[]` and `tach_divisor`. The single `tach_divisor` is shared across channels even though writes occur per channel, so a user writing `fanN_div` changes the divisor used for later RPM conversion globally. There is no cache of RPM values.

## Dependencies And Integration Points
The driver depends on platform resources, device tree compatibles `aspeed,ast2600-pwm-tach` and `aspeed,ast2700-pwm-tach`, clock and reset frameworks, PWM framework, hwmon with-info APIs, and child-node tach channel descriptions.

## Risks
PWM period/duty changes can still glitch as described in the file comments. Tach RPM conversion can divide by zero if a full measurement reports a zero raw tach value; the read path checks only the full-measurement bit before conversion. Shared `tach_divisor` can produce incorrect RPM if channels use different divisors. Probe returns success without hwmon when `aspeed_create_fan_monitor()` fails, because it warns and returns 0.

## Test Signals
Test PWM get/apply calculations for 0, partial, and 100 percent duty; period clamping and `-ERANGE`; polarity inversion; reset assert on cleanup; child `tach-ch` parsing; tach visibility; fan divisor validation; RPM conversion for no full measurement and representative raw counts; multi-channel divisor behavior; and probe behavior on malformed child nodes.
