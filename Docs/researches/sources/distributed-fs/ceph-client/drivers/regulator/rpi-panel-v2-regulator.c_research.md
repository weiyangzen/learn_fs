# sources/distributed-fs/ceph-client/drivers/regulator/rpi-panel-v2-regulator.c

Purpose: supports the Raspberry Pi 7-inch V2 touchscreen microcontroller as an I2C-backed GPIO and PWM provider. Despite the filename, it does not register a regulator; power/reset bits are exposed through `gpio-regmap` and backlight control through a PWM chip.

Important APIs/types/functions: `rpi_panel_v2_pwm_apply()` maps PWM enable and relative duty cycle to `REG_PWM` bits. `rpi_panel_v2_i2c_probe()` allocates a one-channel `pwm_chip`, initializes the I2C regmap, clears `REG_POWERON`, registers a two-line gpio-regmap, stores regmap client data, and adds the PWM chip. `rpi_panel_v2_i2c_shutdown()` clears PWM and power/reset state.

Control flow: PWM apply rejects non-normal polarity, writes zero when disabled, or writes `PWM_BL_ENABLE | duty` when enabled. Probe creates regmap-backed GPIOs for LCD and CTP reset bits, then exposes PWM after GPIO registration succeeds. Shutdown always turns backlight and power/reset bits off.

State and persistence: no private state beyond regmap pointer storage in the PWM chip and I2C client data. Hardware register state is volatile and reset on shutdown.

Dependencies and integration: depends on I2C, regmap, `gpio-regmap`, PWM framework, and OF compatible `raspberrypi,touchscreen-panel-regulator-v2`. Display and touch drivers consume GPIO and PWM resources.

Risks and test signals: because GPIO and PWM share one regmap, probe order and shutdown behavior matter. There is no firmware ID validation despite a defined `REG_ID`. Tests should cover PWM duty scaling, polarity rejection, GPIO set/clear through gpio-regmap, shutdown clearing, and missing regmap/GPIO registration failures.
