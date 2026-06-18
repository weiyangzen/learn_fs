<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/instmem/Kbuild -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/instmem/Kbuild

## Purpose
Adds the instance-memory base plus generation implementations to nvkm-y.

## Important APIs, Types, And Functions
Entries include base.o, nv04.o, nv40.o, nv50.o, gk20a.o, and gh100.o.

## Control Flow
No runtime flow; controls link inclusion.

## State, Persistence, Dependencies, And Integration
State is build configuration. Dependencies are Nouveau Kbuild. Integration points are device-specific instmem constructor availability.

## Risks And Test Signals
Risks: omitting a generation object breaks device probe. Test signals are successful build and symbol resolution for all listed constructors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/instmem/Kbuild -->
