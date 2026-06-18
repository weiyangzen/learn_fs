<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/priv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/priv.h

## Purpose
Defines the private nvkm_i2c function table and shared helper declarations used by all I2C generation implementations.

## Important APIs, Types, And Functions
Important type is nvkm_i2c_func with pad_x_new, pad_s_new, aux count, aux_stat, aux_mask, and aux_autodpcd hooks. It declares nvkm_i2c_new_, g94/gk104 aux stat/mask helpers, and nvkm_i2c container macro.

## Control Flow
No executable flow exists. base.c consumes this table to construct pads/buses/AUX and handle interrupts/autodpcd.

## State, Persistence, Dependencies, And Integration
State is API contract. Dependencies are subdev/i2c.h and BIOS/display core types. Integration points are all generation frontend files and auxch.h.

## Risks And Test Signals
Risks: optional hooks must be NULL-checked consistently; aux count must match hardware/backend support. Test signals are compile coverage and runtime probe on generations with and without AUX hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/priv.h -->
