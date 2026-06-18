# sources/distributed-fs/ceph-client/drivers/thermal/broadcom/bcm2835_thermal.c

## Purpose
Broadcom BCM2835/2836/2837 temperature sensor driver. It maps TSENS registers, enables a clock, registers an OF thermal zone, optionally initializes hardware when firmware has not done so, exposes hwmon, and provides debugfs register access.

## Important APIs, Types, and Functions
- `struct bcm2835_thermal_data` holds zone, MMIO base, clock, and debugfs directory.
- `bcm2835_thermal_adc2temp()` and `bcm2835_thermal_temp2adc()` convert between ADC code and millicelsius using thermal-zone slope/offset.
- `bcm2835_thermal_get_temp()` reads `TSENSSTAT`, requires `VALID`, masks the 10-bit data field, and converts it.
- `bcm2835_thermal_debugfs()` creates a `bcm2835_thermal/regset` debugfs view.
- `bcm2835_thermal_probe()` maps registers, enables the clock, warns on clock-rate deviations, registers the OF zone, initializes `TSENSCTL` if reset is still asserted, adds hwmon and debugfs.
- `bcm2835_thermal_remove()` removes debugfs recursively.

## Control Flow
Probe verifies OF match, maps resource 0, enables the unnamed clock, registers zone id 0, then checks `TSENSCTL_RSTB`. If the firmware did not enable the block, it reads critical trip temperature, configures bandgap, regulator, reset delay, and threshold ADC, writes control once without and once with reset deasserted. Temperature reads are direct MMIO reads with validity checks.

## State and Persistence
The driver stores mapped register and clock handles, the thermal zone pointer, and debugfs directory. Hardware control register state persists in the sensor until reconfigured or reset.

## Dependencies and Integration Points
Depends on OF address/platform resources, common clock framework, thermal OF bindings for slope/offset and critical trip, debugfs, and `thermal_hwmon`.

## Risks and Edge Cases
- If no critical trip exists and firmware left the block disabled, probe fails because threshold programming requires a critical trip.
- Clock outside 1.92-5 MHz only warns, so marginal hardware timing can persist.
- Debugfs allocation failure is tolerated, but debugfs directory can still exist without a regset.
- Slope/offset are trusted from DT.

## Test Signals
Probe tests should cover firmware-initialized and driver-initialized paths, clock-rate warning path, missing critical trip, invalid `TSENSSTAT`, ADC clamp behavior in `temp2adc()`, and debugfs cleanup on remove.
