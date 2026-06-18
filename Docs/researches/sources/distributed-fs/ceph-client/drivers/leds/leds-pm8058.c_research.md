# sources/distributed-fs/ceph-client/drivers/leds/leds-pm8058.c

Purpose: Qualcomm PM8058 LED driver for common, keypad, and flash LED register fields.

Important APIs/types/functions: `struct pm8058_led` stores parent regmap, register offset, LED type, and class device. `pm8058_led_set()` and `pm8058_led_get()` map brightness into 5-bit or 4-bit fields depending on LED type. Probe parses match data and `reg`, applies default state, and registers the LED.

Control flow: platform probe gets parent regmap, reads register offset, configures callbacks and max brightness, applies `default-state` (`on`, `keep`, or off), sets suspend/resume flag for keypad/flash, then registers with LED init data.

State and persistence: state is hardware register bits; `keep` reads current hardware brightness into LED core. No explicit remove-time state change.

Dependencies and integration: depends on parent regmap, OF compatibles `qcom,pm8058-led`, `qcom,pm8058-keypad-led`, `qcom,pm8058-flash-led`, LED class, and PM suspend/resume flags.

Risks: brightness callback is non-blocking but performs regmap I/O and cannot report errors. Invalid `ledtype` silently uses zero mask/value. Register field masks assume board `reg` points to the correct PMIC field.

Test signals: all three compatible types, max brightness 31 vs 15, default-state on/off/keep, get/set field round trip, missing regmap/register errors, and suspend/resume LED state behavior.
