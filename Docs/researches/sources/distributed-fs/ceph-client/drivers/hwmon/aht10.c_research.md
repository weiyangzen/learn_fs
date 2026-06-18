# sources/distributed-fs/ceph-client/drivers/hwmon/aht10.c

## Purpose
This is an I2C hwmon driver for Aosong AHT10, AHT20, and DHT20 temperature and humidity sensors. It exposes one temperature input, one humidity input, and a writable chip update interval through the modern `hwmon_device_register_with_info()` interface.

## Important APIs, Types, And Functions
The driver is centered on `struct aht10_data`, which stores the `i2c_client`, poll interval, previous poll time, cached temperature and humidity, measurement frame size, CRC use, and variant-specific initialization command. Device matching uses `aht10_id` and `aht10_of_match`, with enum variants `aht10`, `aht20`, and `dht20`.

`aht10_probe()` checks `I2C_FUNC_I2C`, allocates state with `devm_kzalloc()`, selects variant behavior, initializes the chip, performs an initial reading, and registers hwmon channels. `aht10_init()` sends the variant init command and checks the busy bit. `aht10_read_values()` sends measurement command `0xac 0x33 0x00`, waits, reads 6 or 7 bytes, validates optional AHT20/DHT20 CRC8, decodes 20-bit humidity and temperature, and updates cached millipercent and millidegree values. `aht10_hwmon_read()`, `aht10_hwmon_write()`, and `aht10_hwmon_visible()` implement the hwmon callbacks.

## Control Flow And State
Probe performs one-time setup and immediately populates cached sensor values. Runtime reads flow through hwmon callbacks to `aht10_temperature1_read()` or `aht10_humidity1_read()`, both of which call `aht10_read_values()`. The driver rate-limits physical sensor transactions through `aht10_polltime_expired()`: if the configured interval has not elapsed, it returns cached readings instead of touching the bus.

State is per device and devm-managed. There is no explicit mutex, so concurrent sysfs reads can race through `previous_poll_time`, `temperature`, and `humidity`; in practice the accesses are simple scalar updates, but duplicated I2C transactions are possible. Persistence is limited to hardware configuration and cached in-memory readings. The writable update interval is clamped to at least 2000 ms and is not stored across driver reloads.

## Dependencies And Integration Points
The driver depends on Linux I2C core APIs, hwmon with-info APIs, `ktime`, `usleep_range()`, and `crc8` helpers. It integrates through I2C IDs and Open Firmware compatibles `aosong,aht10`, `aosong,aht20`, and `aosong,dht20`.

## Risks
The main operational risks are timing-sensitive sensor transactions, CRC failure handling for AHT20/DHT20, and lack of serialization around cached state. `aht10_init()` treats any one-byte status read other than exactly one byte as `-ENODATA`, and a busy status as `-EBUSY`; marginal hardware could fail probe. Because reads return cached data during the poll interval, test expectations must account for stale values after changing environmental conditions.

## Test Signals
Useful tests are probe with each compatible/device ID, sysfs reads of `temp1_input`, `humidity1_input`, and `update_interval`, update interval writes below and above 2000 ms, simulated short I2C reads, CRC mismatch on 7-byte frames, and verification that two immediate reads do not generate a second measurement transaction while reads after the interval do.
