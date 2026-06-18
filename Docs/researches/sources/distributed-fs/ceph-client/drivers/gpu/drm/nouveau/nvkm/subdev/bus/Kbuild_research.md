<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bus/Kbuild -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bus/Kbuild

### Purpose

Build manifest for NVKM bus subdevice support.

### Important APIs, types, and functions

Adds `base.o`, `hwsq.o`, and bus implementations for `nv04`, `nv31`, `nv50`, `g94`, and `gf100` to `nvkm-y`.

### Control flow

No runtime flow; Kbuild aggregates the bus core, hardware sequencer, and generation-specific interrupt/init handlers.

### State and persistence behavior

No runtime state. Build composition determines which `*_bus_new()` constructors and HWSQ helpers are available.

### Dependencies and integration points

Depends on parent Nouveau Kbuild. Device chipset selection code links against the constructors listed here.

### Risks

Missing objects cause unresolved constructors or missing interrupt support for a GPU generation.

### Test signals

Source read size: 8 lines, 262 bytes. Nouveau build, allmodconfig, and link checks for bus constructors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bus/Kbuild -->
