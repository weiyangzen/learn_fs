# sources/distributed-fs/ceph-client/drivers/hwmon/peci/common.h

Purpose: small shared PECI hwmon cache helper header used by CPU and DIMM temperature clients.

Important APIs/types/functions: `PECI_HWMON_UPDATE_INTERVAL` sets a one-second cache interval. `struct peci_sensor_state` stores validity and last-update jiffies. `struct peci_sensor_data` stores a milli-unit sensor value plus update state. `peci_sensor_need_update()` checks validity and staleness. `peci_sensor_mark_updated()` records a successful refresh.

Control flow: PECI clients call `peci_sensor_need_update()` before expensive PECI transactions and call `peci_sensor_mark_updated()` after storing a new value. The helper is inline and header-only.

State and persistence: cache state is embedded by callers in per-sensor structures. Values survive across hwmon read callbacks until the one-second interval expires or the device is removed.

Dependencies and integration: depends on Linux types, `jiffies`, and `time_after()` availability through included kernel headers in users. It is included by both `cputemp.c` and `dimmtemp.c`.

Risks: the comment parameter names mention `sensor`, while functions take `state`; this is cosmetic. The helper does not include `<linux/jiffies.h>` itself, so users must already include it. Cache interval is fixed for all PECI sensors.

Test signals: compile coverage through both PECI drivers, repeated hwmon reads reusing cached values within HZ, and refresh after the interval.
