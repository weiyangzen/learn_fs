# sources/distributed-fs/ceph-client/drivers/leds/rgb/leds-lp5812.h

Purpose: private header for the LP5812 LED driver. It centralizes register addresses, bit constants, mode names, packed configuration unions, and driver state structures.

Important APIs, types, and functions: register defines cover device enable/configuration, update, LED enables, fault clear, manual/auto DC/PWM bases, and status registers. `union lp5812_scan_order` and `union lp5812_drive_mode` provide byte-level register packing. `struct lp5812_mode_mapping` describes text-to-mode mappings. `struct lp5812_led_config`, `struct lp5812_chip`, and `struct lp5812_led` define parsed firmware config, chip-wide state, and per-LED state.

Control flow: no executable logic is present. The C file consumes constants and structures to parse device tree, program mode registers, and register LED class devices.

State and persistence: state definitions include parsed channel count, label, scan mode string, mutex, I2C client, drive-mode register byte, and per-LED brightness/class devices.

Dependencies and integration points: includes LED, multicolor, I2C, mutex, sysfs, and type headers. The header is local to the RGB driver directory.

Risks and test signals: build tests catch structure/constant drift. Driver tests should ensure bitfield packing matches the datasheet for compiler assumptions, and that arrays sized by `LED_COLOR_ID_MAX` are large enough for all parsed color channels.
