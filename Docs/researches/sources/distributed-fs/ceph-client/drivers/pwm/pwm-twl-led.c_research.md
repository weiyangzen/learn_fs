# sources/distributed-fs/ceph-client/drivers/pwm/pwm-twl-led.c

## Purpose

`pwm-twl-led.c` exposes TWL4030/TWL6030 LED PWM terminals through the PWM framework. TWL4030 has two LED PWM outputs; TWL6030 has one LEDPWM output.

## APIs, control flow, and state

TWL4030 config writes LED module on/off-cycle values and enable toggles `LEDEN` LED/PWM bits. TWL6030 config writes `LED_PWM_CTRL1`, enable/disable changes LED mode in `LED_PWM_CTRL2`, request forces software-off mode, and free restores hardware mode. Apply rejects unsupported polarity, configures relative duty, and enables if needed.

No private state is allocated; PMIC registers hold state and no `.get_state` is implemented.

## Dependencies and integration points

The driver uses TWL MFD I2C helpers, `twl_class_is_4030()`, OF compatibles for TWL4030/TWL6030 PWMLED, and the PWM core.

## Risks and test signals

Hardware cannot represent true 0 duty in PWM mode; disabled state should be used for fully off. I2C failures can leave partial state. TWL6030 polarity validation compares to current state. Test duty endpoints, request/free mode transitions, disabled output, I2C errors, and consumer behavior without readback.
