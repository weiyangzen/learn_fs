# sources/distributed-fs/ceph-client/drivers/power/supply/max8998_charger.c

Purpose: implements the MAX8998/LP3974 battery-control platform subdriver. It reports basic battery presence, charger online state, and charging status, and programs charger end-of-charge, restart, and timeout thresholds from parent platform data.

Important APIs/types/functions: `struct max8998_battery_data` stores the parent PMIC device and battery supply. `max8998_battery_get_property()` reads `STATUS2` to expose `PRESENT`, `ONLINE`, and `STATUS`. `max8998_battery_probe()` validates platform data and writes `CHGR1`/`CHGR2` fields for EOC, restart level, and full timeout.

Control flow: probe requires parent platform init data, allocates state, validates EOC range or leaves it unchanged, maps restart values of 100/150/200 mV, disabled, or unchanged to register bits, maps timeout values of 5/6/7 hours, disabled, or unchanged, then registers the battery supply. Property reads always fetch fresh PMIC status over the parent I2C helper.

State and persistence: the driver caches no dynamic charger status. Charger thresholds are stored in PMIC registers and can remain until PMIC reset. Platform data is the only configuration source.

Dependencies and integration: depends on MAX8998 MFD helper functions, platform device data, and power-supply core. Matching is platform ID `max8998-battery`.

Risks: some `max8998_update_reg()` calls in the restart/timeout switch are not checked immediately; later failures may be missed. No extcon/regulator control or notifications are implemented. Probe fails when platform data is absent, so DT-only systems need parent translation. Test signals include valid/invalid platform settings, unchanged/disabled sentinel values, property bit mappings, I2C update failures, and module autoload through platform alias.
