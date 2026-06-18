<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bus/base.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bus/base.c

### Purpose

Generic NVKM bus subdevice wrapper. It adapts generation-specific bus functions to the NVKM subdevice lifecycle.

### Important APIs, types, and functions

`nvkm_bus_new_()` allocates and constructs a bus object; `nvkm_bus_init()` and `nvkm_bus_intr()` dispatch to `bus->func`; `nvkm_bus_dtor()` returns the object for freeing.

### Control flow

Construction installs the common `nvkm_subdev_func` table and the generation-specific `nvkm_bus_func`. Init and interrupt callbacks are thin dispatchers.

### State and persistence behavior

`struct nvkm_bus` persists as the device bus subdevice and stores only the function table plus embedded subdev.

### Dependencies and integration points

Depends on `priv.h`, NVKM allocation helpers, and subdevice lifecycle. Generation files call `nvkm_bus_new_()`.

### Risks

No null checks around required callbacks, so generation function tables must provide valid init/intr methods when used.

### Test signals

Source read size: 64 lines, 1984 bytes. Build/link tests and boot-time init/interrupt dispatch on each bus generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bus/base.c -->
