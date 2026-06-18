<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/bus.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/bus.h

## Purpose
Declares the backend function table and constructors/destructors for nvkm I2C bus objects plus generation-specific bus constructors and logging macros.

## Important APIs, Types, And Functions
Important type is nvkm_i2c_bus_func with init, drive_scl, drive_sda, sense_scl, sense_sda, and xfer hooks. Declarations include nvkm_i2c_bus_ctor/new_/del/init/fini, nvkm_i2c_bit_xfer, nv04/nv4e/nv50/gf119 bus constructors, and BUS_* macros.

## Control Flow
No executable control flow is present. Implementations fill this function table to expose either line-level bit-bang support or backend xfer support to bus.c.

## State, Persistence, Dependencies, And Integration
State is API contract only. Dependencies are pad.h and Linux i2c_msg through included headers. Integration points are bus.c, bit.c, and all bus*.c implementations.

## Risks And Test Signals
Risks: backends must provide a coherent set of hooks; drive_scl without intended bit-algo selection changes adapter behavior. Test signals are compile coverage and working DDC/I2C transfers on each generation-specific bus.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/bus.h -->
