# sources/distributed-fs/ceph-client/drivers/hwmon/sht3x.c

Purpose: I2C hwmon driver for Sensirion SHT3x/SHT85 humidity-temperature sensors and STS3x temperature-only sensors. It supports single-shot and periodic measurement modes, repeatability selection, heater control, alarms, writable limits, update interval, and debugfs serial number.

Important APIs/types/functions: `struct sht3x_data` stores mode, selected command, wait time, repeatability, cached readings/limits, serial number, and two mutexes. `sht3x_read_from_command()` serializes I2C command/response. `sht3x_update_client()` refreshes cached readings. `limits_update()` and `limit_write()` read/write packed temp/humidity limits with CRC. Hwmon callbacks cover chip/temp/humidity attributes.

Control flow: probe requires full I2C, clears status, initializes data and CRC table, waits for limit-read readiness, caches limits, registers hwmon, and reads serial debugfs value. Update interval writes break periodic mode if needed, start the selected periodic command, update mode, and select read command.

State and persistence: readings are cached according to selected update interval; single-shot mode refreshes on every read due zero interval. Limit arrays mirror device limit registers. Repeatability and mode persist in driver and device until changed.

Dependencies/integration: I2C master transfers, hwmon info API, debugfs, CRC8, jiffies timing.

Risks: response CRC is not checked for normal reads/status/limits, though CRC is generated for writes. `heater_enable_store()` returns raw `i2c_master_send()` byte count instead of `count` on success. `repeatability_store()` does not reselect commands or restart periodic mode immediately.

Test signals: single-shot waits by repeatability, periodic mode transitions and break command, humidity hidden for STS3x, limit write/read round trips, alarm/status bits, heater control return behavior, and serial debugfs creation.
