<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/padgm200.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/padgm200.c

## Purpose
Implements GM200 shared-pad mode programming and pad constructors using GF119 bus and GM200 AUX backends.

## Important APIs, Types, And Functions
Important APIs are gm200_i2c_pad_s_new and gm200_i2c_pad_x_new; internal helper is gm200_i2c_pad_mode.

## Control Flow
Mode programming writes GM200 registers 0x00d970 and 0x00d97c per hybrid pad to select OFF/I2C/AUX. Shared pads include mode hook; external pads do not.

## State, Persistence, Dependencies, And Integration
State is pad mode and GM200 hardware selection bits. Dependencies are pad.h, auxch.h, bus.h, gf119_i2c_bus_new, and gm200_i2c_aux_new. Integration points are gm200_i2c frontend.

## Risks And Test Signals
Risks: register offset must match GM200 display block and native path is bypassed under GSP-RM. Test signals are DDC/AUX transfers on non-GSP GM200 and correct shared-pad arbitration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/padgm200.c -->
