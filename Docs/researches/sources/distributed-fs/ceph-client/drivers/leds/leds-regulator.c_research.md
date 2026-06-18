# sources/distributed-fs/ceph-client/drivers/leds/leds-regulator.c

Purpose: LED class driver for LEDs powered directly by a regulator. It can treat the regulator as binary on/off or, when multiple voltage selectors are available, map brightness levels onto regulator voltages.

Important APIs, types, and functions: `struct regulator_led` stores `led_classdev`, mutex, enabled flag, and `struct regulator *vcc`. `led_regulator_get_max_brightness()` probes voltage-count capability. `led_regulator_get_voltage()` maps brightness to `regulator_list_voltage(brightness - 1)`. `regulator_led_brightness_set()` handles all brightness updates, and probe/register/remove wire the device into LED and regulator frameworks.

Control flow: probe gets exclusive `vled`, allocates state, derives `max_brightness`, accepts legacy platform-data name/default brightness, and registers with `led_classdev_register_ext()`. Brightness off disables the regulator. Nonzero brightness optionally programs a voltage first, then enables the supply.

State and persistence: in-memory `enabled` shadows regulator state and is initialized from `regulator_is_enabled()`. The driver does not persist brightness beyond LED core state. Remove unregisters the LED and disables the regulator.

Dependencies and integration points: integrates with regulator consumers, platform devices, LED class, fwnode naming, legacy `leds-regulator.h` platform data, and OF compatible `regulator-led`.

Risks and test signals: voltage selector math assumes brightness value N maps to selector N-1 and relies on regulator APIs returning valid voltages. Validate binary regulators, multi-voltage regulators, already-enabled supplies at probe, platform-data brightness bounds, suspend/resume flag behavior, and cleanup disabling the regulator.
