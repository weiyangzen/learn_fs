# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega20_powertune.h

## Purpose
`vega20_powertune.h` declares the public Vega20 PowerTune helpers used by the hardware-manager implementation and generic callback wiring.

## Important APIs, Types, and Functions
It declares `vega20_set_power_limit()`, `vega20_power_control_set_level()`, and `vega20_validate_power_level_request()`. These are implemented in `vega20_powertune.c` and operate on `struct pp_hwmgr`.

## Control Flow
The header has no control flow. It permits `vega20_hwmgr.c` to call PowerTune setup during DPM enable and to expose power-limit programming through `pp_hwmgr_func`.

## State and Persistence
No state is declared. The functions operate on `hwmgr->backend`, platform descriptor fields, and SMU runtime state.

## Dependencies and Integration Points
The declarations rely on `struct pp_hwmgr` being visible to includers. The implementation requires SMU message helpers and Vega20 feature-state definitions.

## Risks
Because this header only declares a narrow interface, most risk is signature drift with the implementation or generic hwmgr callback expectations.

## Test Signals
Build success validates declaration/definition consistency. Runtime power-limit and power-control sysfs behavior validates the API.
