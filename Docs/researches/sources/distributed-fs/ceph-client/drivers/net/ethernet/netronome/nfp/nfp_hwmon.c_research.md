# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_hwmon.c

## Purpose
Registers an hwmon device for NFP sensors exposed by NSP, providing chip temperature and assembly power readings plus static max/critical thresholds.

## Important APIs, Types, and Functions
- `nfp_hwmon_sensor_id()` maps hwmon temp/power channels to NSP sensor IDs.
- `nfp_hwmon_read()` returns constant thresholds or reads live sensor values with `nfp_hwmon_read_sensor()` if the NSP sensor mask advertises the sensor.
- `nfp_hwmon_is_visible()` exposes read-only temp and power attributes.
- `nfp_hwmon_register()` conditionally registers `hwmon_device_register_with_info()` when HWMON is reachable and NSP sensor data exists.
- `nfp_hwmon_unregister()` unregisters the hwmon device on PF cleanup.

## Control Flow
PF probe calls register after network probe succeeds. Registration skips cleanly when HWMON is unavailable, NSP identify data is absent, or no sensors are advertised. Reads are routed by hwmon core to the static ops table.

## State and Persistence Behavior
Stores the registered hwmon device pointer in `pf->hwmon_dev`. Sensor values are read from NSP at request time; thresholds are constants. No persistence.

## Dependencies and Integration Points
Depends on Linux hwmon, NSP sensor IDs/read API, PF state in `nfp_main.h`, and `pf->nspi->sensor_mask`.

## Risks
Sensor channel mapping is fixed: one temperature channel and three power channels derived from `NFP_SENSOR_ASSEMBLY_POWER + channel`. If firmware changes channel ordering, readings could be mislabeled. Registration silently skips in several cases, so absence may be expected rather than fatal.

## Test Signals
Probe with/without CONFIG_HWMON, missing NSP info, zero sensor mask, partial sensor mask, and active temperature/power reads. Validate sysfs attributes and threshold values in millidegrees/microwatts.
