<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/iccsense/Kbuild -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/iccsense/Kbuild

## Purpose
Adds ICC sense base and GF100 frontend objects to nvkm-y.

## Important APIs, Types, And Functions
Entries are nvkm/subdev/iccsense/base.o and gf100.o.

## Control Flow
No runtime control flow; it controls link inclusion.

## State, Persistence, Dependencies, And Integration
State is build configuration. Dependencies are Nouveau Kbuild. Integration points are kernel build and GF100 iccsense constructor availability.

## Risks And Test Signals
Risks: missing objects remove power sensor support. Test signals are successful build and gf100_iccsense_new symbol availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/iccsense/Kbuild -->
