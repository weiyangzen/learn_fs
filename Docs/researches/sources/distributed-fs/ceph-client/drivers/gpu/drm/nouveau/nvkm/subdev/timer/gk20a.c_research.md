# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/timer/gk20a.c

## Purpose
Provides GK20A timer construction by reusing NV04-compatible timer operations.

## Important APIs, Types, And Functions
`gk20a_timer_new()` passes a static function table to `nvkm_timer_new_()` using `nv04_timer_intr`, `nv04_timer_read`, `nv04_timer_time`, `nv04_timer_alarm_init`, and `nv04_timer_alarm_fini`.

## Control Flow
Construction allocates the common timer object; all runtime behavior is delegated to NV04-style register handlers.

## State, Persistence, And Dependencies
State is the common timer object and the NV04-compatible hardware timer registers.

## Integration Points
Integrates Tegra GK20A device setup with the generic timer base and NV04 register accessors.

## Risks
Assumes GK20A timer registers match NV04 semantics. Any SoC-specific clock difference is not handled here.

## Test Signals
Signals are functioning timer alarms on GK20A, especially PMU DVFS and thermal polling alarms.
