# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/therm/fantog.c

## Purpose
Implements a software PWM fan backend by toggling a GPIO at a fixed period.

## Important APIs, Types, And Functions
`struct nvkm_fantog` carries a private alarm, lock, period, target percent, and GPIO function. `nvkm_fantog_create()`, `nvkm_fantog_set()`, `nvkm_fantog_get()`, and the alarm callback drive the backend.

## Control Flow
Set disables hardware PWM if present, stores the target, flips the fan GPIO, and schedules the next toggle according to the requested duty cycle over a 100 ms period.

## State, Persistence, And Dependencies
State is the allocated toggle fan object, its target percent, timer alarm, and GPIO output level. No persistent storage exists.

## Integration Points
Used as a fallback from `nvkm_therm_fan_ctor()` when PWM backend creation fails but a drivable fan GPIO exists.

## Risks
Software PWM depends on timer precision and can jitter. The code uses generic DCB fan GPIO lookup in updates rather than only the saved function, so GPIO metadata consistency matters.

## Test Signals
Signals include visible GPIO toggling, target percent readback, fan speed changes, and no timer-alarm leaks on suspend.
