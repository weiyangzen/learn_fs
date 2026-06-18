<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/auxgf119.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/auxgf119.c

## Purpose
Provides a GF119 AUX backend wrapper that reuses the G94 transfer implementation while enabling address-only AUX transactions.

## Important APIs, Types, And Functions
Important object is gf119_i2c_aux and constructor gf119_i2c_aux_new, which calls g94_i2c_aux_new_.

## Control Flow
No independent transfer flow exists; all hardware operations delegate to g94_i2c_aux_xfer with address_only set true.

## State, Persistence, Dependencies, And Integration
State is the base g94_i2c_aux object created by g94_i2c_aux_new_. Dependencies are auxch.h and auxg94.c. Integration points are GF119 pad constructors and GF119/GK/GPU generations using the G94-style AUX register block.

## Risks And Test Signals
Risks: assumes GF119 register layout is compatible with G94 while changing address-only semantics. Test signals are address-only DPCD operations and normal AUX reads/writes on GF119-class hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/auxgf119.c -->
