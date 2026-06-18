# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/include/linux/atomisp_gmin_platform.h

## Purpose
This header declares the G-Min platform integration helpers used by AtomISP sensor drivers on Intel MID/Atom camera platforms. It provides the bridge from a sensor V4L2 subdev to platform data, registration, variable lookup, and removal.

## Important APIs, Types, And Functions
- `atomisp_register_i2c_module()` registers a sensor subdev and its `camera_sensor_platform_data` with AtomISP.
- `atomisp_gmin_remove_subdev()` removes a G-Min-managed subdev.
- `gmin_get_var_int()` reads integer platform variables, likely from ACPI/device properties, with a default fallback.
- `gmin_camera_platform_data()` creates or returns `camera_sensor_platform_data` for a subdev using a declared CSI input format and Bayer order.

## Control Flow
Sensor probes call `gmin_camera_platform_data()` to obtain platform callbacks, use those callbacks during sensor configuration, then call `atomisp_register_i2c_module()` after V4L2/media initialization. Remove and failure paths call `atomisp_gmin_remove_subdev()`.

## State And Persistence
The header declares APIs only. Runtime state is held by the G-Min platform implementation and the returned `camera_sensor_platform_data`. No disk persistence is involved.

## Dependencies And Integration Points
It includes `atomisp_platform.h`, so it depends on V4L2 subdevs, AtomISP input formats, Bayer order enums, and camera platform data. It is the key integration point used by sensor drivers such as OV2722 to avoid board-specific hardcoding.

## Risks
- Sensor drivers assume returned platform callbacks are complete; missing callback validation can lead to null calls.
- Platform-variable defaults can mask ACPI/property misconfiguration.
- Removal must match registration exactly to avoid dangling subdev pointers in AtomISP platform tables.

## Test Signals
Tests should cover platform-data creation for supported sensors, default variable lookup, missing-property fallback, registration/removal idempotence on probe failure paths, and callback behavior for rails, GPIOs, FLIS clock, and CSI configuration.
