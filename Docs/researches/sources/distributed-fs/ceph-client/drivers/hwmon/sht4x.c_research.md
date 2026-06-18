
# sources/distributed-fs/ceph-client/drivers/hwmon/sht4x.c

Purpose: I2C hwmon driver for Sensirion SHT4x humidity and temperature sensors. It exports `temp1_input`, `humidity1_input`, `update_interval`, plus custom heater controls for enable, power, and duration.

Important APIs, types, and functions: `struct sht4x_data` stores the I2C client, cached readings, jiffy timestamps, and heater state. `sht4x_read_values()` issues high precision measurements, waits for conversion or heater completion, receives six bytes, validates Sensirion CRC8 words, and converts raw ticks to millidegrees and millipercent. `sht4x_hwmon_read()`, `sht4x_hwmon_write()`, and `sht4x_hwmon_visible()` implement the hwmon callbacks; `heater_*_show/store()` implement extra sysfs attributes.

Control flow, state, and persistence: probe requires full I2C, initializes CRC table, resets the sensor, sets default interval 2000 ms and heater 200 mW for 1000 ms, then registers with `devm_hwmon_device_register_with_info()`. Runtime state is in memory only. Temperature and humidity are cached until `update_interval` expires, while heater mode tracks `heating_complete` and `data_pending` in jiffies.

Dependencies and integration points: uses I2C core, hwmon core, `hwmon-sysfs`, jiffies, sleep helpers, and Linux CRC8 support. Device matching is via I2C id `sht4x` and OF compatible `sensirion,sht4x`.

Risks and test signals: there is no mutex around cache and heater state, so concurrent sysfs reads/writes can race in theory. Heater enable only accepts writes of true and returns `-EBUSY` while active. Test with successful probe/reset, CRC failure injection, interval clamping, heater command selection, short I2C transfers returning `-ENODATA` or `-EIO`, and repeated reads proving cache suppression before the interval expires.
