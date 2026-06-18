# sources/distributed-fs/ceph-client/drivers/leds/leds-max77650.c

Purpose: LED driver for MAX77650/MAX77651 charger and power-supply PMIC LEDs.

Important APIs/types/functions: `struct max77650_led` stores LED class device, parent regmap, and two per-LED registers. `max77650_led_brightness_set()` updates brightness and enable bits in register A. `max77650_led_probe()` parses up to three child LEDs, registers them, initializes LED A/B defaults, and enables the top-level LED master bit.

Control flow: probe obtains parent regmap, validates child count and `reg`, maps each `reg` to A/B register offsets, registers with extended LED init data, writes per-channel defaults, then writes `MAX77650_REG_CNFG_LED_TOP`. Brightness zero disables the LED; nonzero writes enable bits plus 5-bit brightness.

State and persistence: state is in PMIC registers; no software brightness cache beyond LED core. Probe resets LED channel registers to defaults.

Dependencies and integration: depends on MAX77650 MFD regmap, platform-device child, firmware-node LED properties, and LED class.

Risks: duplicate child `reg` values reuse the same array slot without explicit duplicate detection. Register B is initialized but not otherwise used by brightness set. Only 5-bit brightness is exposed.

Test signals: child count validation, invalid/duplicate reg behavior, brightness 0/max register writes, top-level enable bit, and probe failure when parent regmap is missing.
