# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega20_thermal.h

## Purpose
`vega20_thermal.h` declares Vega20 thermal and fan-control helpers and shared constants for the hwmgr thermal callback wiring.

## Important APIs, Types, and Functions
It defines `struct vega20_temperature` with edge, hotspot, HBM, VR, liquid, and PLX temperature fields, alert masks, minimum/maximum temperature ranges, and fan static-mode constants. It declares temperature read, fan speed info/get/set for PWM and RPM, SMU fan-control start/stop, thermal alert disable, thermal controller start, and thermal controller stop functions.

## Control Flow
The header has no executable control flow. `vega20_hwmgr.c` installs the declared routines in `pp_hwmgr_func`, while `vega20_thermal.c` implements them.

## State and Persistence
No state is stored here. The declared functions mutate SMU feature state and THM registers through `struct pp_hwmgr`.

## Dependencies and Integration Points
It includes `hwmgr.h` for `struct pp_hwmgr`, `struct phm_fan_speed_info`, and `struct PP_TemperatureRange`. It is included by both the thermal implementation and hwmgr backend.

## Risks
The declared `struct vega20_temperature` is broader than the current implementation's direct temperature reads, so callers should not assume every field is populated by these APIs. Constants must match hardware register mode encodings.

## Test Signals
Build linkage plus fan/thermal sysfs and hwmon behavior validate this header's interface.
