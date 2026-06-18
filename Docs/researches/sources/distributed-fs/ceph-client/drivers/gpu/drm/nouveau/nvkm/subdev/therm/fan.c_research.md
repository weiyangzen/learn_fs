# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/therm/fan.c

## Purpose
Implements common fan target handling, fan backend discovery, tachometer sensing, and BIOS-derived fan defaults.

## Important APIs, Types, And Functions
Key functions are `nvkm_therm_fan_get()`, `nvkm_therm_fan_set()`, `nvkm_therm_fan_sense()`, `nvkm_therm_fan_user_get()`, `nvkm_therm_fan_user_set()`, `nvkm_therm_fan_ctor()`, `nvkm_therm_fan_init()`, and `nvkm_therm_fan_fini()`.

## Control Flow
`nvkm_fan_update()` clamps targets to BIOS min/max, compares current duty, smooths changes by 3 percent steps unless immediate, invokes backend `set`, and schedules another timer alarm until target duty is reached. Constructor chooses PWM, toggle, or nil backend and parses BIOS fan tables.

## State, Persistence, And Dependencies
State is `struct nvkm_fan`: BIOS/perf data, current target percent, alarm, lock, tach GPIO, and backend callbacks.

## Integration Points
Depends on GPIO discovery, BIOS fan tables, timer alarms, chip PWM callbacks, and optional chip tachometer callbacks.

## Risks
Manual writes are rejected outside manual mode. Tachometer fallback busy-waits with sleep ranges and assumes four GPIO transitions per revolution. Bad BIOS limits can clamp fan behavior despite safety checks.

## Test Signals
Signals include fan backend type logs, RPM readings, smooth fan ramp behavior, suspend alarm cancellation, and successful user fan set/get in manual mode.
