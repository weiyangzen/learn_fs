# sources/distributed-fs/ceph-client/drivers/leds/leds-mc13783.c

Purpose: LED driver for Freescale/NXP MC13783, MC13892, and MC34708 PMIC LED controller blocks.

Important APIs/types/functions: device-type descriptors define LED ID ranges, register counts, and LEDCTRL base offsets. `mc13xxx_max_brightness()` derives per-output brightness width. `mc13xxx_led_set()` maps each logical LED ID to register and bit shift. `mc13xxx_led_probe_dt()` parses `led-control` and child LED nodes. `mc13xxx_led_probe()` initializes control registers and registers LED class devices.

Control flow: platform driver probe gets parent `mc13xxx`, selects device type from platform ID, parses DT or platform data, writes initial LED control registers, validates IDs and duplicates, then registers each LED with suspend/resume flag. Brightness writes perform register read-modify-write with masks based on maximum brightness width.

State and persistence: LED state resides in PMIC registers; driver stores LED IDs and parent pointers. Initial control register values come from board data/DT and are written on probe.

Dependencies and integration: depends on `linux/mfd/mc13xxx.h`, MC13xxx register helpers, platform IDs, optional OF parsing from parent `leds` node, and LED class.

Risks: probe cleanup uses manual unregister because registrations are not devm-managed. Duplicate or invalid IDs abort registration after warning/error. `BUG()` is used for impossible LED IDs in brightness path, so bad internal state is fatal.

Test signals: DT `led-control` array size per chip, ID mapping for all supported PMIC variants, brightness masks for 4/5/6-bit outputs, duplicate ID handling, and remove-time unregister.
