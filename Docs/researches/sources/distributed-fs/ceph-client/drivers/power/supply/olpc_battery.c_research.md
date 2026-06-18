
# sources/distributed-fs/ceph-client/drivers/power/supply/olpc_battery.c

## Purpose
This driver exposes OLPC XO AC and battery information from the OLPC embedded controller through the generic power_supply class. It supports older and newer EC protocols, XO-1 and XO-1.5 battery property sets, raw EEPROM access, EC error visibility, and EC wake sources for suspend.

## Important APIs, Types, and Functions
`struct olpc_battery_data` stores the AC and battery power supplies, serial buffer, and protocol endian flags. AC status comes from `olpc_ac_get_prop()`. Battery helpers include `olpc_bat_get_status()`, `olpc_bat_get_health()`, `olpc_bat_get_mfr()`, `olpc_bat_get_tech()`, design-charge/voltage helpers, `ecword_to_cpu()`, and `olpc_bat_get_property()`. Probe and PM entry points are `olpc_battery_probe()` and `olpc_battery_suspend()`.

## Control Flow
Probe allocates state, queries `EC_FIRMWARE_REV`, derives protocol flags from DT and EC revision, checks battery status once, registers `olpc_ac`, selects XO-1 or XO-1.5 battery property arrays, then registers `olpc_battery` with extra sysfs groups. Every battery property read first fetches EC battery status, rejects most properties if no battery is present, and then issues specific `olpc_ec_cmd()` calls for voltage, current, SOC, temperature, ACR, EEPROM manufacturer/type, serial, or error code. Suspend maps power-supply wakeup settings onto EC SCI wake sources.

## State and Persistence
The driver caches only the serial string and protocol flags. Battery measurements, presence, health, and AC status are read live from the EC. The binary `eeprom` sysfs file reads directly from EC EEPROM address range 0x20-0x7f and does not cache. There is no write path or persistent kernel-side state.

## Dependencies and Integration Points
It depends on `olpc_ec_cmd()`, `olpc_ec_wakeup_*()` helpers, Open Firmware compatibles `olpc,xo1-battery`, `olpc,xo1.5-battery`, and `olpc,xo1.75-ec`, and the power_supply core. Extra attributes are attached through `power_supply_config.attr_grp`.

## Risks and Test Signals
Risks include EC protocol/revision mismatches, endian conversion mistakes, stale EC last-known data after battery removal, and global mutation of the static `olpc_bat_desc` property pointer during probe. Tests should verify EC command scaling formulas, absent-battery behavior returning `-ENODEV`, XO-1 vs XO-1.5 property visibility, EEPROM/error sysfs reads, wakeup source programming in suspend, and old EC revision rejection.
