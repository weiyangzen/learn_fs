# sources/distributed-fs/ceph-client/drivers/net/phy/aquantia/aquantia_hwmon.c

## Purpose
Adds HWMON temperature support for Aquantia PHYs, exposing current temperature, warning/failure thresholds, and alarm bits.

## Important APIs, Types, and Functions
Key callbacks are `aqr_hwmon_is_visible`, `aqr_hwmon_read`, `aqr_hwmon_write`, and exported `aqr_hwmon_probe`. Helpers include `aqr_hwmon_get`, `aqr_hwmon_set`, `aqr_hwmon_test_bit`, and `aqr_hwmon_status1`. The HWMON channel table exposes chip timezone registration and temperature attributes.

## Control Flow and State
Read operations verify the sensor type, optionally check the valid bit before reading current temperature, convert signed 16-bit 1/256 degree Celsius values to millidegrees, and return alarm bits from general status. Write operations range-check threshold values to signed 8-bit degree limits represented in millidegrees, convert to register units, and write vendor thermal provisioning registers. Probe sanitizes the MDIO device name to alphanumeric characters and registers a devm HWMON device.

## Dependencies and Integration Points
Depends on `CONFIG_HWMON`, phylib MMD reads/writes, HWMON core, thermal register definitions from `aquantia.h`, and `devm_hwmon_device_register_with_info`. It is called from `aqr107_probe` when HWMON is reachable.

## Risks and Test Signals
Risks include returning `-EBUSY` if the valid bit is not set, incorrect signed temperature conversion, threshold range rejection surprising users, and sanitized-name collisions. Test signals include `sensors` output, reading current temperature under valid/invalid conditions, writing min/max/critical thresholds, alarm-bit changes, and builds with HWMON disabled.
