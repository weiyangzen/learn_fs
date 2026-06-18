<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/Kbuild -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/Kbuild

### Purpose

Build manifest for the Nouveau NVKM VBIOS parser objects. It ensures all table parsers, shadowing backends, init-script interpreter, and newer memory/power table readers are linked into the NVKM module.

### Important APIs, types, and functions

Adds `base.o`, `bit.o`, table readers such as `dcb.o`, `dp.o`, `pll.o`, `rammap.o`, `timing.o`, `volt.o`, shadow backends, and the newer `M0203.o`, `M0205.o`, `M0209.o`, and `P0260.o` objects to `nvkm-y`.

### Control flow

Kbuild has no runtime control flow; kernel build aggregation compiles every listed source into the Nouveau object set.

### State and persistence behavior

No runtime state. The persistent effect is build composition: omitting a line removes exported parser helpers and can break link or runtime VBIOS discovery.

### Dependencies and integration points

Depends on the parent Nouveau Kbuild including this directory. It integrates all `subdev/bios/*.h` declared helpers with display, memory, clock, therm, and power-management code.

### Risks

Missing objects lead to unresolved symbols or silent loss of table support. Ordering is not semantically important, but stale entries can break incremental builds.

### Test signals

Source read size: 41 lines, 1442 bytes. Kernel `make drivers/gpu/drm/nouveau/`, allmodconfig build, and symbol checks for exported parser helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/Kbuild -->
