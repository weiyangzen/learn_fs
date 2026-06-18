# sources/distributed-fs/ceph-client/drivers/leds/rgb/leds-lp5812.c

Purpose: I2C driver for TI LP5812, a matrix RGB LED driver with direct, time-coded, and mix drive modes. This implementation registers single-color and multicolor LED class devices and uses manual PWM/DC controls.

Important APIs, types, and functions: low-level `lp5812_write()`/`lp5812_read()` implement the chip's 10-bit register addressing by folding high address bits into the I2C address. `parse_drive_mode()` maps DT/sysfs-style mode strings to drive mode and scan-order fields. `lp5812_set_led_mode()`, `lp5812_manual_dc_pwm_control()`, `lp5812_set_brightness()`, and `lp5812_set_mc_brightness()` program channel mode and PWM. DT parsing is split across `lp5812_parse_led_channel()`, `lp5812_parse_led()`, and `lp5812_of_probe()`.

Control flow: probe parses child LED definitions and optional `ti,scan-mode`, initializes the chip, allocates LED objects, and registers each channel. Initialization enables the device, sets safety thresholds, programs drive mode/scan order, and commits configuration with `LP5812_CMD_UPDATE`. Registration writes max current to auto/manual DC registers, puts LEDs in manual mode, and enables each LED output.

State and persistence: `struct lp5812_chip` stores parsed channel config, mode, scan order, and mutex. Hardware registers hold enable, manual PWM/DC, and drive configuration. Remove disables LED enable registers and device enable.

Dependencies and integration points: raw I2C transfers, LED/multicolor class, OF properties, mutex locking, and local `leds-lp5812.h` definitions.

Risks and test signals: test 10-bit register-address encoding, scan-mode string coverage, config-update error bit handling, single versus child-channel multicolor parsing, max-current unit conversion, output-enable bit packing, and remove-time deinit. The code stores LED pointers in `dev->platform_data`, so check for unintended conflicts.
