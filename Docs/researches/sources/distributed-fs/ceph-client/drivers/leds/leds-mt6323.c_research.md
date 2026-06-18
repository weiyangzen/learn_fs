# sources/distributed-fs/ceph-client/drivers/leds/leds-mt6323.c

Purpose: MediaTek MT6323/MT6331/MT6332 PMIC LED and WLED driver using parent `mt6397` regmap.

Important APIs/types/functions: hardware descriptors `mt6323_regs`, `mt6323_hwspec`, and `mt6323_data` describe register layouts and limits. `mt6323_led_set_brightness()`, `mt6323_led_set_blink()`, and `mt6323_get_led_hw_brightness()` manage ISINK LEDs. `mt6323_wled_set_brightness()` and WLED helpers manage paired WLED channels. Probe parses child `reg` and `mediatek,is-wled`.

Control flow: probe enables the common 32 kHz clock, allocates controller state, validates each child `reg`, selects normal LED or WLED callbacks, applies default-state, and registers extended LED class devices. Normal LED on enables clock source, channel clock, channel enable, brightness, full duty, and default period. Off disables channel and clock. Blink programs duty and period if within hardware limits.

State and persistence: `current_brightness` caches requested brightness, while hardware registers hold real enable, clock, duty, and brightness state. Remove turns LEDs off and disables the common clock, but iterates only contiguous `leds->led[i]` entries from zero.

Dependencies and integration: depends on MT6397/MT6323 MFD regmap, OF compatible match data, LED class, and PMIC clock/register layout.

Risks: `mt6323_led_hw_brightness()` subtracts one from brightness, so callers must avoid zero there. Remove loop can miss non-contiguous registered LED IDs. WLED brightness does not program an analog brightness register; it only toggles channel pair and cache. Blink duty math and max period vary by hardware spec.

Test signals: DT coverage for MT6323, MT6331, and MT6332; normal LED on/off/get/blink; WLED pair enable/disable; default-state `on`, `off`, and `keep`; non-contiguous `reg` remove behavior; and regmap error paths.
