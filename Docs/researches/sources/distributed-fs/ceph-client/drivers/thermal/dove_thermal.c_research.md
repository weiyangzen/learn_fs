# sources/distributed-fs/ceph-client/drivers/thermal/dove_thermal.c

## Purpose
Marvell Dove thermal sensor driver. It initializes the thermal diode registers, registers a tripless thermal zone, and reports temperature from status/control MMIO resources.

## Important APIs, Types, and Functions
- `struct dove_thermal_priv` stores sensor and control MMIO bases.
- `dove_init_sensor()` programs averaging, reference calibration, calibration voltage, resets and enables the sensor, then polls for the first nonzero reading.
- `dove_get_temp()` checks the valid bit in control register 1, extracts the 9-bit sensor sample, and computes temperature with the documented formula.
- Probe maps two resources, initializes hardware, registers/enables a tripless zone, and stores it in drvdata.

## Control Flow
Probe allocates private data, maps sensor and control resources, initializes the sensor, registers `dove_thermal`, enables the thermal zone, and stores the zone pointer. Reads first validate the diode-control status bit, then convert the sample from the sensor register.

## State and Persistence
Driver state is MMIO mappings and the thermal zone pointer. Calibration and enable bits persist in hardware after `dove_init_sensor()`.

## Dependencies and Integration Points
Depends on platform MMIO resources, OF compatible `marvell,dove-thermal`, and the thermal core tripless zone API.

## Risks and Edge Cases
- Initialization polls up to one million tight iterations without sleep.
- A zero sensor value is treated as not ready during init, which could be ambiguous depending on hardware.
- Conversion uses large integer constants; unit mistakes would have large reporting impact.
- No runtime PM or remove-time hardware disable is implemented.

## Test Signals
Tests should cover successful initialization writes, timeout path, invalid status bit returning `-EIO`, conversion fixture values, thermal zone enable failure cleanup, and resource mapping failure.
