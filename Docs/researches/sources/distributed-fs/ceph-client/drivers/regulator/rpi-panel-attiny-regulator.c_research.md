# sources/distributed-fs/ceph-client/drivers/regulator/rpi-panel-attiny-regulator.c

Purpose: controls the Raspberry Pi 7-inch touchscreen panel's Atmel microcontroller, exposing panel power as a regulator, brightness as a backlight, and two reset lines as GPIOs.

Important APIs/types/functions: `struct attiny_lcd` stores the regmap, serialized port state cache, GPIO chip, and mutex. Regulator ops are `attiny_lcd_power_enable()`, `attiny_lcd_power_disable()`, and `attiny_lcd_power_is_enabled()`. Backlight updates use `attiny_update_status()`. GPIO output is handled by `attiny_gpio_set()`, including a bridge programming sequence after bridge reset release. `attiny_i2c_probe()` initializes all subsystems.

Control flow: probe allocates state, initializes a custom regmap, validates firmware ID `0xde` or `0xc3`, powers down PWM/power, registers the regulator, registers a raw backlight, and registers a sleeping GPIO chip. Enabling the regulator writes port registers in a timed sequence: resets held, orientation configured, panel power on, resets released after delays. Disable reverses PWM, ports, and resets.

State and persistence: `port_states[]` caches output register state because GPIO operations compose bit masks. `gpio_states[]` is allocated but not used for reads. Hardware state is volatile microcontroller register state; driver does not persist settings across unload or reset.

Dependencies and integration: integrates I2C, regmap, regulator, backlight, gpiochip, OF matching, and panel/bridge consumers. The regulator constraints permit status changes only.

Risks and test signals: timing and cached port state are critical. `attiny_lcd_power_is_enabled()` reads live hardware while other operations use cached state, and several regmap writes ignore return values in sequencing paths. Test signals include probe ID rejection, repeated I2C transient failures, regulator enable/disable sequencing, GPIO reset behavior, bridge post-reset programming, backlight writes, and concurrent backlight/GPIO/regulator access under the mutex.
