# sources/distributed-fs/ceph-client/drivers/hwmon/lenovo-ec-sensors.c

## Purpose
`lenovo-ec-sensors.c` exposes temperature and fan telemetry from Lenovo ThinkStation embedded-controller registers. Supported product families have model-specific channel maps and labels for CPU, DIMM, chassis, PSU, and fan readings.

## Important APIs, types, and functions
The driver uses DMI matching, platform device bundling, raw I/O ports, region reservation, mutex locking, and hwmon sysfs registration. `get_ec_reg()` implements Microchip EMI register access through fixed ports around `0x0900`. `struct ec_sensors_data` stores labels, maps, and the EC mutex. `lenovo_ec_do_read_temp()` converts EC temperature bytes from an offset encoding. `lenovo_ec_do_read_fan()` reads 16-bit fan current/max values. `lenovo_ec_hwmon_read_string()` supplies labels.

## Control flow
Module init checks the DMI table and creates a bundled platform device/driver. Probe allocates state, requests the EMI I/O region, initializes the EC address window, verifies the signature bytes `MCHP`, selects per-family temp/fan maps and hwmon channel info from DMI driver data, and registers the hwmon device. Runtime reads map the public hwmon channel index to an EC channel index, then perform one or two port reads under the mutex.

## State and persistence
The driver maintains only mapping pointers and the mutex. It does not cache sensor values. It writes the EMI application ID/address registers as part of each read transaction, but does not persistently configure thresholds or fan policy. The global `lenovo_ec_chip_info.info` pointer is mutated at probe according to system type.

## Dependencies and integration points
It depends on exact Lenovo DMI product codes, the Microchip EMI I/O window at `0x0900`, and hwmon sysfs. It also assumes a single supported system instance because of global platform device and chip-info state.

## Risks
Raw I/O region lifetime is partly manual: probe calls `request_region()` and module exit releases it, with explicit release on some error paths. The signature check uses `&&` between byte mismatches, which means it rejects only if all four bytes differ; this is weaker than requiring all four bytes to match. DMI driver data is dereferenced after `dmi_first_match()` without a null check, relying on module init gating. Product maps and label arrays must stay aligned with channel info counts.

## Test signals
Test all DMI product-code families, MCHP signature failure paths, region request failure, temp `-ENODATA` for low encoded values, fan input/max reads, label alignment, mutexed concurrent reads, module unload region release, and map bounds against each channel-info table.
