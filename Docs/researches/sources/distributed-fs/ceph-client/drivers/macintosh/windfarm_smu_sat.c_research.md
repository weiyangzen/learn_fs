# sources/distributed-fs/ceph-client/drivers/macintosh/windfarm_smu_sat.c

## Purpose
Implements Windfarm sensors for SMU satellite I2C controllers and exports `smu_sat_get_sdb_partition()` so model drivers can fetch per-core calibration partitions from satellite controllers.

## Important APIs, Types, And Functions
`struct wf_sat` stores satellite identity, I2C client, OF node, sensor list, cache, timestamp, kref, and mutex. `struct wf_sat_sensor` maps a cooked sensor index, optional second index for power, shift, and embedded `wf_sensor`. `smu_sat_get_sdb_partition()` selects a partition by ID, reads its length, fetches 4-byte blocks with byte swapping, and returns a newly allocated `smu_sdbp_header` buffer. `wf_sat_sensor_get()` refreshes a 16-byte cache when older than 800 ms and converts voltage/current/temp/power values.

## Control Flow
Probe scans child nodes for cooked sensor registers `0x30..0x37` with `location` strings like `CPU A0 ...`, determines chip/core, registers `cpu-voltage-N`, `cpu-current-N`, and `cpu-temp-N`, then synthesizes `cpu-power-N` when both voltage and current indices exist for a core. Remove unregisters all sensors and releases the satellite.

## State, Dependencies, And Integration
Global `sats[2]` allows platform code such as PM112 to fetch SAT partitions by chip ID. Per-satellite cache avoids excessive I2C traffic. Dependencies include I2C SMBus block/word access, OF properties, Windfarm sensor registration, krefs, and mutexes.

## Risks And Test Signals
The partition reader returns allocated memory that callers must free, and it does not attach discovered partitions to the device tree despite a TODO. Probe assumes at most one CPU chip per SAT and specific `CPU [AB][01]` location strings. Test signals include cache refresh timing, power sensor synthesis, byte-order correctness in partition reads, missing partition handling, two-satellite registration in `sats[]`, and remove-time sensor/kref cleanup.
