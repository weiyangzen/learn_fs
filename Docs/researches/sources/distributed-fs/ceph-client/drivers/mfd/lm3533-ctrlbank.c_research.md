# sources/distributed-fs/ceph-client/drivers/mfd/lm3533-ctrlbank.c

Purpose: shared LM3533 control-bank helper library used by LM3533 backlight/LED children. It abstracts per-bank enable, current limit, brightness, and PWM-mask registers.

Important APIs/types/functions: exported `lm3533_ctrlbank_enable()`, `lm3533_ctrlbank_disable()`, `lm3533_ctrlbank_set_max_current()`, `lm3533_ctrlbank_set_brightness()`, `lm3533_ctrlbank_get_brightness()`, `lm3533_ctrlbank_set_pwm()`, and `lm3533_ctrlbank_get_pwm()`.

Control flow: helpers compute register offsets from the control-bank id and call parent `lm3533_read()`, `lm3533_write()`, or `lm3533_update()`. Enable/disable update one bit in the global control-bank enable register. Brightness and PWM access bank-specific registers.

State and persistence: no private state; it operates on `struct lm3533_ctrlbank`, which references the parent core, device, and bank id. Hardware registers hold brightness/current/PWM/enable state.

Dependencies and integration: depends on `linux/mfd/lm3533.h` parent helpers and is consumed by LM3533 child drivers rather than registering a device itself.

Risks: bank id validity is assumed for most helpers and must be established by callers/platform data. Current and PWM setters validate ranges; brightness does not constrain beyond `u8`.

Test signals: backlight/LED child calls for enable/disable, max-current boundary values, PWM values above `0x3f` returning `-EINVAL`, brightness readback, and regmap failure propagation.
