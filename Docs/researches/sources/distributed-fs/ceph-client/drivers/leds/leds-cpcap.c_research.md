# sources/distributed-fs/ceph-client/drivers/leds/leds-cpcap.c

Purpose: CPCAP MFD child LED driver for Motorola CPCAP red, green, blue, auxiliary display, and camera privacy LEDs. It exposes one LED class device per platform child selected by OF compatible data.

Important APIs/types/functions: `struct cpcap_led_info` describes register, mask, brightness limit, and optional init bits; `struct cpcap_led` stores classdev, parent regmap, regulator, mutex, and power state. `cpcap_led_val()` packs 5-bit current and 4-bit duty. `cpcap_led_set_power()` wraps `regulator_enable/disable()`. `cpcap_led_set()` is the blocking brightness callback. `cpcap_led_probe()` resolves `device_get_match_data()`, parent `regmap`, `vdd`, `label`, optional init writes, and calls `devm_led_classdev_register()`.

Control flow: probe is table-driven by `cpcap_led_of_match`; brightness ON enables `vdd`, writes current/duty, and brightness OFF first writes `CPCAP_LED_NO_CURRENT`, then duty off, then disables `vdd`. Init masks are applied before registration for ADL and CP variants.

State and persistence: runtime state is volatile in CPCAP registers and `led->powered`; there is no persisted configuration. The mutex serializes power and register updates. Devm handles lifetime, but there is no explicit shutdown callback, so final LED state depends on LED core cleanup and last brightness state.

Dependencies/integration: depends on CPCAP MFD register definitions, parent regmap, regulator framework, OF match data, and LED class. Device tree must provide compatible-specific child nodes and a `label`.

Risks: label is mandatory; missing parent regmap or `vdd` aborts probe. OFF sequencing is hardware-specific and should not be reordered. Regulator state can become stale if a register write fails after enabling. There is no suspend/resume flag or retain-state policy.

Test signals: instantiate each compatible, verify regulator toggles only when needed, check OFF writes current cutoff before duty off, inject regmap/regulator failures, and confirm `max_brightness` is 31 or 1 as expected.
