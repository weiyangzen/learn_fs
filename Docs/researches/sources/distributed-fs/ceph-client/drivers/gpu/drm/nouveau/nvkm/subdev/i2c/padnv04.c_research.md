<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/padnv04.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/padnv04.c

## Purpose
Defines a minimal NV04 pad function table capable of creating NV04 legacy bit-bang buses.

## Important APIs, Types, And Functions
Important object is nv04_i2c_pad_func and API nv04_i2c_pad_new.

## Control Flow
Constructor delegates to nvkm_i2c_pad_new_ with bus_new_0 = nv04_i2c_bus_new.

## State, Persistence, Dependencies, And Integration
State is common pad state only. Dependencies are pad.h and bus.h. Integration points are nv04_i2c_new and legacy CCB entries.

## Risks And Test Signals
Risks: no mode hook/AUX support. Test signals are NV04 DDC bus creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/padnv04.c -->
