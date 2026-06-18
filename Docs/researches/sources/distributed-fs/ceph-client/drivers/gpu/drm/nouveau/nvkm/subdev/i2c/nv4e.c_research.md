<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/nv4e.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/nv4e.c

## Purpose
Defines the NV4E I2C subdev with NV4E pad creation only.

## Important APIs, Types, And Functions
Important object is nv4e_i2c and constructor nv4e_i2c_new.

## Control Flow
Constructor delegates to nvkm_i2c_new_ with pad_x_new = nv4e_i2c_pad_new.

## State, Persistence, Dependencies, And Integration
State is common I2C lists. Dependencies are priv.h/pad.h. Integration points are NV4E DCB I2C bus creation.

## Risks And Test Signals
Risks: no AUX support. Test signals are DDC transfers on NV4E hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/nv4e.c -->
