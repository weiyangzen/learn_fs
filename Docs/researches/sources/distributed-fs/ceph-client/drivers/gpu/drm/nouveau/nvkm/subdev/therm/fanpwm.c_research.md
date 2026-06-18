# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/therm/fanpwm.c

## Purpose
Implements the PWM fan backend using chip-specific PWM callbacks and GPIO polarity information.

## Important APIs, Types, And Functions
`struct nvkm_fanpwm` extends `nvkm_fan` with the DCB GPIO function. `nvkm_fanpwm_create()`, `nvkm_fanpwm_get()`, and `nvkm_fanpwm_set()` are the key operations.

## Control Flow
Create validates `NvFanPWM`, rejects toggle-mode BIOS fans, and requires chip PWM support. Get reads div/duty through `pwm_get` when enabled or falls back to GPIO level. Set computes divisor from BIOS PWM frequency or perf divisor, handles inverted polarity, programs duty, and enables PWM control.

## State, Persistence, And Dependencies
State includes fan BIOS/perf parameters and the selected GPIO function; hardware state is PWM divisor, duty, and mux enable registers owned by chip callbacks.

## Integration Points
Depends on BIOS fan parsing, GPIO metadata, `nvkm_boolopt()`, and chip implementations in nv40/nv50/gf119/gm107 paths.

## Risks
Duty calculation depends on polarity bits and valid divisors. PWM frequency of zero falls back to perf divisor; invalid BIOS data can produce poor fan behavior.

## Test Signals
Signals are correct duty percent readback, PWM enablement on supported GPIOs, and fallback to toggle/nil when PWM is unavailable.
