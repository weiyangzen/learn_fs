# sources/distributed-fs/ceph-client/drivers/hwmon/ibmpex.c

## Purpose

`ibmpex.c` exposes IBM PowerExecutive BMC temperature and power sensors through hwmon. It discovers supported BMCs through IPMI, filters firmware sensor names for power and temperature signatures, creates classic hwmon sysfs attributes for current, lowest, and highest values, and provides a write-only reset for high/low history.

## Important APIs, Types, and Functions

`struct ibmpex_bmc_data` holds per-BMC hwmon state, IPMI transport fields, cached firmware version, sensor count, and an array of `struct ibmpex_sensor_data`. Each sensor stores whether it is exported, three cached values, a multiplier, and three `sensor_device_attribute_2` entries. `ibmpex_ver_check()`, `ibmpex_query_sensor_count()`, `ibmpex_query_sensor_name()`, `ibmpex_query_sensor_data()`, and `ibmpex_reset_high_low_data()` implement the PowerExecutive command set. `ibmpex_find_sensors()` classifies sensor names and creates attributes. `ibmpex_update_device()` refreshes all active sensors under a mutex. `ibmpex_msg_handler()` completes synchronous IPMI requests.

## Control Flow

Module init registers an IPMI SMI watcher. On BMC registration, the driver allocates `ibmpex_bmc_data`, creates an IPMI user, initializes the command message, checks the PowerExecutive version, registers the BMC device with hwmon, links the BMC into the global list, and discovers sensors. Discovery queries the count, reads each name, identifies names starting with `pwr` or `tem`, chooses units, and creates three attributes per exported sensor. Sysfs reads call `ibmpex_update_device()`, which refreshes active sensors every two seconds by querying data and extracting current/low/high fields at fixed offsets. BMC removal reverses attribute creation, unregisters hwmon and IPMI, and frees names and arrays.

## State and Persistence Behavior

The driver caches sensor data in `values[3]` with `valid` and `last_updated` gating. Sensor names are not retained beyond classification; generated sysfs attribute names are dynamically allocated and freed. The high/low reset write sends a firmware command and does not parse user input. There is no persistent storage outside BMC-maintained high/low state.

## Dependencies and Integration Points

It depends on IPMI SMI watcher and user APIs, classic hwmon sysfs helpers, mutexes, jiffies, endian extraction, and BMC device driver data. The hwmon device is registered against the BMC device itself rather than an extra platform device. IBM System x DMI aliases support module autoloading.

## Risks and Edge Cases

IPMI waits use `wait_for_completion()` without timeout, so a lost response can block probe or sysfs reads indefinitely. Completion state is not reinitialized per transaction. `ibmpex_send_message()` return values are ignored in query helpers. `ibmpex_msg_handler()` copies received payload into a fixed `IPMI_MAX_MSG_LENGTH` buffer without clamping to that buffer, trusting IPMI message bounds. The reset-high-low store ignores user value and always returns success after sending. Dynamic sysfs names are limited by a fixed 32-byte allocation but generated names fit current formats. Unsupported sensor names are silently skipped, so firmware naming changes can hide sensors.

## Test Signals

Test version-check rejection, sensor-count errors, malformed sensor names, power multiplier selection for version 1 versus version 2 and watt signatures, sysfs cleanup on mid-discovery failure, high/low reset command emission, stale cache reuse within two seconds, sensor data short-read handling, and BMC disappearance during active sysfs reads.
