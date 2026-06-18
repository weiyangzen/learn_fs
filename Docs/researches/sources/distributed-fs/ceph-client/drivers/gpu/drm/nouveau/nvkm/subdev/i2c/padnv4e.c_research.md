<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/padnv4e.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/padnv4e.c

## Purpose
Defines a minimal NV4E pad function table capable of creating NV4E MMIO bit-bang buses.

## Important APIs, Types, And Functions
Important object is nv4e_i2c_pad_func and API nv4e_i2c_pad_new.

## Control Flow
Constructor delegates to nvkm_i2c_pad_new_ with bus_new_4 = nv4e_i2c_bus_new.

## State, Persistence, Dependencies, And Integration
State is common pad state only. Dependencies are pad.h and bus.h. Integration points are nv4e_i2c_new.

## Risks And Test Signals
Risks: no AUX/shared mode support. Test signals are NV4E DDC bus creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/padnv4e.c -->
