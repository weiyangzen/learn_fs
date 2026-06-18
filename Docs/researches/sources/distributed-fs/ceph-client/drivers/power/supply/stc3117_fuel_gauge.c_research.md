# sources/distributed-fs/ceph-client/drivers/power/supply/stc3117_fuel_gauge.c

## Purpose
STMicroelectronics STC3117 fuel-gauge driver. It initializes the gauge from battery info and shunt-resistor properties, keeps chip RAM state with CRC, periodically refreshes measurements, and exposes battery status, voltage, current, OCV, average current, capacity, temperature, and presence.

## Important APIs, Types, and Functions
`union stc3117_internal_ram` models the 16-byte RAM area with testword, HRSOC, config values, SOC, state, and CRC. `struct stc3117_data` stores regmap, delayed work, power supply, battery parameters, config values, and latest measurements. Key functions are `stc3117_probe()`, `stc3117_init()`, `stc3117_set_para()`, `stc3117_task()`, `stc3117_get_battery_data()`, `ram_read()`, `ram_write()`, and `fuel_gauge_update_work()`.

## Control Flow
Probe initializes regmap, CRC table, power supply, reads `shunt-resistor-micro-ohms` and battery info, calls `stc3117_init()`, creates delayed work, and schedules it immediately. Init validates device ID, computes CC/VM config values, validates RAM testword/CRC, programs OCV/SOC tables and configuration, restores SOC when valid, and stores a new CRC. The periodic task refreshes measurements, repairs invalid RAM, handles battery failure/POR, restarts the gauge if needed, updates state, writes HRSOC/SOC/CRC, and reschedules after 2 seconds.

## State and Persistence
Persistent-ish state lives in the STC3117 internal RAM and is guarded by CRC8. Software caches latest measurements in `struct stc3117_data` for property reads. There is no separate kernel mutex around property reads versus update work.

## Dependencies and Integration Points
Depends on I2C, regmap, power_supply battery-info, devm delayed work, CRC8 helpers, and firmware `shunt-resistor-micro-ohms`. Compatible string is `st,stc3117`.

## Risks and Test Signals
Bulk register reads ignore return values in some paths, signed current conversion appears to treat raw 16-bit values as unsigned, and property reads race with update work. `power_supply_put_battery_info()` is not called after reading battery info. Test RAM CRC recovery, POR/BATFAIL paths, work cancellation, signed current interpretation, missing battery info, shunt scaling, and concurrent sysfs reads during update.
