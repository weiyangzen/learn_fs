<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bus/priv.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bus/priv.h

### Purpose

Private bus subdevice header. It defines the generation-specific bus callback contract and shared constructor prototype.

### Important APIs, types, and functions

`struct nvkm_bus_func` contains `init`, `intr`, optional `hwsq_exec`, and `hwsq_size`. It declares `nvkm_bus_new_()`, `nv50_bus_init()`, and `nv50_bus_intr()`.

### Control flow

No runtime control flow. Generation files populate this table, and `base.c` dispatches through it.

### State and persistence behavior

No state by itself. The callback table controls persistent behavior of each bus object.

### Dependencies and integration points

Depends on `subdev/bus.h` and NVKM device/subdev types. Included by all bus implementation files.

### Risks

Changing the callback contract affects every generation. Missing required callbacks lead to null dispatch at runtime.

### Test signals

Source read size: 19 lines, 549 bytes. Compile coverage and boot/init/interrupt tests for every bus generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bus/priv.h -->
