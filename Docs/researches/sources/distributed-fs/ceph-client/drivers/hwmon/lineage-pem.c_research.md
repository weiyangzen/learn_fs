# sources/distributed-fs/ceph-client/drivers/hwmon/lineage-pem.c

## Purpose
`lineage-pem.c` supports Lineage Compact Power Line power entry modules and converters that are nominally PMBus-like but use nonstandard commands. It exposes voltage, current, power, temperature, fan, status, and alarm sysfs attributes through an I2C hwmon driver.

## Important APIs, types, and functions
The driver uses I2C SMBus block reads, legacy hwmon sysfs attribute groups, jiffies caching, and mutexes. `struct pem_data` stores client pointer, optional attribute groups, cached firmware/data/input/fan strings, feature flags, and cache timing. `pem_read_block()` validates fixed-length SMBus block responses. `pem_update_device()` refreshes cached strings once per second and clears information flags. Conversion helpers decode output voltage/current/temp, input voltage/power, and fan speeds. `pem_probe()` detects optional input and fan support.

## Control flow
Probe checks SMBus capabilities, allocates state, reads firmware revision to prove the device is present, clears flags, builds base attribute groups, probes input string support with two possible lengths, probes fan speed support, and registers hwmon groups. Runtime show callbacks call `pem_update_device()`, then decode cached bytes or alarm bits. The cache refresh reads the mandatory data string, optional input string, optional fan speed string, clears info flags, and marks the cache valid.

## State and persistence
The driver caches telemetry for one second. It does not expose writes except the internal clear-info-flags SMBus command during refresh and probe. Optional feature detection persists in `input_length` and `fans_supported` for the life of the driver.

## Dependencies and integration points
It depends on direct I2C access to the PEM, with the file comments recommending use behind a PCA9541 I2C master selector. It does not use the PMBus subsystem because the commands and telemetry format are nonstandard.

## Risks
Fixed-length block reads can fail on devices with variant firmware formats. Clearing info flags after each refresh may acknowledge transient conditions before another monitor reads them. Optional input detection has asymmetric fallback: it tries the 4-byte form first and the 5-byte form only after an error, not after an all-zero successful 4-byte response. Alarm attributes are always exposed even when some measurement groups are absent.

## Test signals
Test firmware read failure, block length mismatch, cache refresh throttling, optional input 4-byte and 5-byte detection, fan support detection, alarm bit decoding, conversion formulas for voltage/current/power/temp/fan values, and behavior behind an I2C mux/master selector.
