<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/padnv50.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/padnv50.c

## Purpose
Defines a minimal NV50 pad function table capable of creating NV50 MMIO bit-bang buses.

## Important APIs, Types, And Functions
Important object is nv50_i2c_pad_func and API nv50_i2c_pad_new.

## Control Flow
Constructor delegates to nvkm_i2c_pad_new_ with bus_new_4 = nv50_i2c_bus_new.

## State, Persistence, Dependencies, And Integration
State is common pad state only. Dependencies are pad.h and bus.h. Integration points are nv50_i2c_new and G94 external pads.

## Risks And Test Signals
Risks: no AUX/shared mode support in this file. Test signals are NV50 DDC bus creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/padnv50.c -->
