<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/amlogic_thermal.c -->
# sources/distributed-fs/ceph-client/drivers/thermal/amlogic_thermal.c

## Purpose

`amlogic_thermal.c` implements the Amlogic G12/A1 thermal sensor driver. It maps the TSENSOR register block through regmap, reads calibration trim data from AO secure syscon, enables the sensor clock and analog/filter bits, converts hardware temperature codes to millicelsius, registers an OF thermal zone, and supports suspend/resume.

## Important APIs, Types, and Functions

`struct amlogic_thermal_soc_calib_data` stores calibration constants `A`, `B`, `m`, and `n`. `struct amlogic_thermal_data` stores the efuse offset, calibration parameter pointer, and regmap config. `struct amlogic_thermal` stores device, data, TSENSOR regmap, AO secure regmap, clock, thermal zone, and trim info.

Core functions are `amlogic_thermal_code_to_millicelsius()`, `amlogic_thermal_initialize()`, `amlogic_thermal_enable()`, `amlogic_thermal_disable()`, `amlogic_thermal_get_temp()`, `amlogic_thermal_probe()`, `amlogic_thermal_remove()`, `amlogic_thermal_suspend()`, and `amlogic_thermal_resume()`. OF match data covers `amlogic,g12a-ddr-thermal`, `amlogic,g12a-cpu-thermal`, and `amlogic,a1-cpu-thermal`.

## Control Flow

Probe allocates state, obtains match data, maps the MMIO resource, initializes a regmap, gets the sensor clock, looks up the `amlogic,ao-secure` syscon, registers a device-tree thermal zone, exposes hwmon sysfs, reads trim info and validates calibration version bits, then enables the clock and sensor config bits. Temperature reads pull `TSENSOR_STAT0`, mask the 16-bit code, and run the documented fixed-point formula with calibration constants and signed trim data. Remove and suspend disable sensor bits and clock; resume reenables them.

## State and Persistence Behavior

State is runtime-only except for read-only efuse trim data in secure AO registers. The driver stores trim info, regmap pointers, clock state, and thermal-zone registration in devm-managed memory. Hardware sensor enable state changes across probe, remove, suspend, and resume.

## Dependencies and Integration Points

The driver depends on platform/OF matching, regmap MMIO, syscon regmap lookup, clocks, thermal OF zone registration, thermal hwmon integration, and Amlogic TSENSOR/AO secure register layout. It is selected by `CONFIG_AMLOGIC_THERMAL` and built by the thermal Makefile.

## Risks and Edge Cases

`of_device_get_match_data()` is not checked before dereferencing, so a bad match table state would crash probe. `regmap_read()` return values are ignored in initialization and temperature reads, so bus/register errors can become stale or bogus temperatures. Calibration validation rejects unsupported trim version bits, which is safer than guessing but can disable thermal reporting on unrecognized SoCs. Signed trim calculation uses bitwise complement plus one on the masked value; it should be validated against the efuse format. The driver does not implement interrupt trips or `set_trips`; thermal polling/governor behavior depends on thermal core configuration.

## Test Signals

Tests should cover all OF compatibles and efuse offsets, missing clock/syscon/MMIO resources, calibration valid and invalid trim versions, positive and negative trim values, conversion formula regression against datasheet examples, temperature read error handling expectations, hwmon registration, suspend/resume clock and bit programming, and removal after failed partial probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thermal/amlogic_thermal.c -->
