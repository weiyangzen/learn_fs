# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/timer/priv.h

## Purpose
Defines private timer callback contracts and shared NV04 helper declarations.

## Important APIs, Types, And Functions
`struct nvkm_timer_func` contains init, interrupt, read, time set, alarm init, and alarm fini callbacks. The header declares `nvkm_timer_new_()`, `nvkm_timer_alarm_trigger()`, and NV04 helper functions.

## Control Flow
Chip timer files populate the callback table and pass it to common construction.

## State, Persistence, And Dependencies
No runtime state exists in the header; it defines the callback ABI for `struct nvkm_timer`.

## Integration Points
Integrates NV04/NV40/NV41/GK20A implementations with the common timer base.

## Risks
Callback signature changes affect all timer chips and alarm users.

## Test Signals
Compile-time coverage and timer subdev construction across chip variants are the main signals.
