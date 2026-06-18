<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/iccsense/priv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/iccsense/priv.h

## Purpose
Declares private sensor and rail structures plus constructors for the ICC sense subdev.

## Important APIs, Types, And Functions
Important types are nvkm_iccsense_sensor with id/type/i2c/addr/config and nvkm_iccsense_rail with read callback/sensor/index/mohm. It declares nvkm_iccsense_ctor and nvkm_iccsense_new_.

## Control Flow
No executable control flow. base.c owns list population and callbacks.

## State, Persistence, Dependencies, And Integration
State is structure layout for sensors/rails. Dependencies are subdev/iccsense.h and BIOS extdev types. Integration points are base.c and gf100.c.

## Risks And Test Signals
Risks: sensor lifetime is tied to iccsense dtor and rail pointers must not outlive sensors. Test signals are clean teardown and no use-after-free under subdev destruction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/iccsense/priv.h -->
