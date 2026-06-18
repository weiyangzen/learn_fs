
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_hwmon.h

## Purpose
Declares the Nouveau hwmon wrapper object and lifecycle functions.

## Important APIs, Types, and Functions
`struct nouveau_hwmon` stores the owning DRM device and the registered hwmon device. `nouveau_hwmon()` returns `nouveau_drm(dev)->hwmon`. The header declares `nouveau_hwmon_init()` and `nouveau_hwmon_fini()`.

## Control Flow
The header provides a simple accessor used by teardown and any code needing the registered hwmon wrapper. Lifecycle control is implemented in `nouveau_hwmon.c` and invoked by the DRM device init/fini sequence.

## State and Persistence
The only defined state is the heap-allocated wrapper stored on the persistent `struct nouveau_drm`. It exists from successful hwmon registration until device teardown.

## Dependencies and Integration Points
Relies on `nouveau_drm()` from the main driver header and on Linux device types. It is included by `nouveau_drm.c` and `nouveau_hwmon.c`.

## Risks and Test Signals
Risks are low and mostly around null handling when hwmon support is disabled or registration skipped. Test signals include init/fini on devices without therm/volt/iccsense and builds with hwmon compiled in, modular, and disabled.
