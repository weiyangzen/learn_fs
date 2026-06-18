# sources/distributed-fs/ceph-client/drivers/leds/leds-lm3642.c

Purpose: platform-data I2C/regmap driver for TI LM3642 flash LED, exposing flash, torch, and indicator class devices plus sysfs control for external torch/strobe pins.

Important APIs/types/functions: `struct lm3642_chip_data` stores three classdevs, brightness caches, pin-enable settings, platform data, regmap, mutex, and last fault. `lm3642_chip_init()` writes initial TX pin enable. `lm3642_control()` reads fault flags, writes current bits, composes mode and external pin bits, and updates `REG_ENABLE`. Brightness callbacks use `guard(mutex)`. `torch_pin_store()` and `strobe_pin_store()` update pin bits.

Control flow: probe requires platform data and I2C, initializes regmap/mutex, copies pin settings, configures chip, registers flash with `strobe_pin` group, torch with `torch_pin` group, and indicator. Remove unregisters all and writes `REG_ENABLE = 0`.

State and persistence: software caches requested brightness and pin flags; hardware stores current, mode, and pin control. Fault register is read on every control call and logged.

Dependencies/integration: platform data `leds-lm3642.h`, I2C regmap, LED class default triggers, cleanup guard mutex helpers.

Risks: platform data is mandatory. Sysfs `torch_pin_store()` and `strobe_pin_store()` use `container_of(..., cdev_indicator)` even when attributes are attached to torch/flash classdevs, which is a suspicious container mismatch. External pin state can alter mode semantics.

Test signals: flash/torch/indicator brightness, pin sysfs writes and container correctness, fault logging, registration unwind paths, and remove-time disable.
