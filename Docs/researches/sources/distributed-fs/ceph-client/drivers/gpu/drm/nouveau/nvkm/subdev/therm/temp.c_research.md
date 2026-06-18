# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/therm/temp.c

## Purpose
Implements common thermal threshold defaults, BIOS sensor parsing, polling-based threshold emulation, and emergency actions.

## Important APIs, Types, And Functions
Important functions include `nvkm_therm_sensor_ctor()`, `nvkm_therm_sensor_preinit()`, `nvkm_therm_sensor_init()`, `nvkm_therm_sensor_fini()`, `nvkm_therm_program_alarms_polling()`, `nvkm_therm_sensor_event()`, and threshold state get/set helpers.

## Control Flow
Constructor sets default thresholds, parses VBIOS sensor data, and enforces minimum hysteresis. Polling checks current temperature once per second, detects rising/falling transitions around hysteresis windows, updates state, and emits fan boost, downclock, pause, or shutdown actions.

## State, Persistence, And Dependencies
State includes BIOS threshold values, per-threshold alarm states, the polling alarm, and optional emergency callbacks in `therm->emergency`.

## Integration Points
Depends on chip `temp_get`, timer alarms, orderly poweroff workqueue, common fan control, and BIOS thermal sensor parsing.

## Risks
Shutdown uses atomic allocation for work; allocation failure means no poweroff is scheduled. Polling only continues while `temp_get` succeeds. Emergency callbacks must tolerate repeated threshold transitions.

## Test Signals
Signals include threshold crossing logs, fan forced to 100 percent on fanboost, downclock/pause callback activation, and polling alarm cancellation on suspend.
