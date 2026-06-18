# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/therm/fannil.c

## Purpose
Provides a dummy fan backend for boards with no controllable fan or externally managed cooling.

## Important APIs, Types, And Functions
`nvkm_fannil_create()` allocates `struct nvkm_fan`, sets type `none / external`, and installs get/set callbacks that return `-ENODEV`.

## Control Flow
Fan constructor falls back here after PWM and toggle creation fail. Later common fan operations see the backend but receive unsupported-operation errors from hardware access.

## State, Persistence, And Dependencies
State is only the allocated fan object and its type/callback fields.

## Integration Points
Integrates with `nvkm_therm_fan_ctor()` as the safe fallback fan backend.

## Risks
Userspace may see fan controls but operations report `-ENODEV`. Automatic fan policy cannot drive cooling through this backend.

## Test Signals
Signals are fallback logs, successful therm construction without fan hardware, and `-ENODEV` on fan get/set paths.
