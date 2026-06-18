# sources/distributed-fs/ceph-client/drivers/thermal/broadcom/bcm2711_thermal.c

## Purpose
Broadcom BCM2711 AVS ring-oscillator thermal sensor driver. It reads a syscon-backed temperature status register, converts the raw code using thermal-zone slope/offset, registers an OF thermal zone, and exposes hwmon sysfs.

## Important APIs, Types, and Functions
- `struct bcm2711_thermal_priv` holds the regmap and thermal zone.
- `bcm2711_get_temp()` reads `AVS_RO_TEMP_STATUS`, checks validity bits, masks the 10-bit data field, and computes `slope * val + offset`.
- `bcm2711_thermal_probe()` gets the parent syscon regmap, registers zone id 0 with `devm_thermal_of_zone_register()`, and calls `thermal_add_hwmon_sysfs()`.
- OF match supports `brcm,bcm2711-thermal`.

## Control Flow
Probe allocates private data, obtains the parent OF node, converts it to a regmap, registers the thermal zone, stores the zone pointer, and adds hwmon files. Every temperature read performs a regmap read and rejects samples where neither validity bit is set.

## State and Persistence
Runtime state is just private regmap and zone pointers. Calibration is not stored locally; slope and offset come from the thermal zone configuration on each read.

## Dependencies and Integration Points
Depends on `MFD_SYSCON`, OF thermal zones, regmap, platform driver core, and `thermal_hwmon`. The hardware register must be in the parent syscon address space.

## Risks and Edge Cases
- The validity check tests the combined validity mask with `if (!(val & mask))`; this accepts either bit rather than requiring both bits.
- Missing or incorrect parent syscon node fails probe.
- Bad DT slope/offset values directly skew temperature reporting.

## Test Signals
Mock regmap tests should cover valid/invalid status bits, raw-code conversion, syscon lookup failure, thermal zone registration failure, and hwmon registration return handling.
