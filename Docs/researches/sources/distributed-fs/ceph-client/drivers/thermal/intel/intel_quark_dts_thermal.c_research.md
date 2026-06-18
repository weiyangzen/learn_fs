# sources/distributed-fs/ceph-client/drivers/thermal/intel/intel_quark_dts_thermal.c

## Purpose

`intel_quark_dts_thermal.c` supports the Intel Quark X1000 digital thermal sensor through IOSF sideband registers, registering one polled thermal zone with hot and critical trips.

## Important APIs, Types, and Functions

`struct soc_sensor_entry` stores lock status, saved trip/enable registers, and thermal zone. `soc_dts_enable()`/`soc_dts_disable()` toggle DTS enable when unlocked. `get_trip_temp()` and `update_trip_temp()` read/write PTPS trip thresholds with the Quark temperature base. Thermal callbacks implement get temp, set trip, and change mode. `alloc_soc_dts()` initializes state and zone; `free_soc_dts()` restores saved registers.

## Control Flow

Module init verifies CPU ID and IOSF availability, then allocates the sensor. Allocation checks lock state, saves defaults when writable, sets writable trip flags only when unlocked, reads trips, registers a polling zone, and enables it. Set-trip clamps unsafe thresholds to 105C before programming. Exit restores enable/PTPS if writable and unregisters the zone.

## State and Persistence Behavior

The global `soc_dts` points to one runtime sensor entry. The driver saves original DTS enable and PTPS registers and restores them on exit unless locked. Polling delay is a module parameter.

## Dependencies and Integration Points

It depends on Quark CPU matching, IOSF MBI, thermal core, and polling thermal zones. It is separate from the newer Baytrail/SoC DTS helper.

## Risks and Test Signals

Risks include Celsius versus millicelsius expectations in trip/temp callbacks, locked register behavior, unsafe threshold clamping, IOSF failures under the shared mutex, and no interrupt support. Test signals include Quark-only module load, locked/unlocked register paths, trip read/write and restore, mode enable/disable, polling updates, and safe threshold clamp.
