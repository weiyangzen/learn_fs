<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/auxgm200.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/auxgm200.c

## Purpose
Implements DP AUX transfers for GM200-style hardware using the 0x00d930/0x00d940/0x00d950/0x00d954/0x00d958 register block and supports address-only transactions.

## Important APIs, Types, And Functions
Important functions are gm200_i2c_aux_init/fini, gm200_i2c_aux_xfer, gm200_i2c_aux_new, and gm200_i2c_aux_func.

## Control Flow
Control flow mirrors g94 AUX: acquire ownership, check sink detect, disable autodpcd, write data for write commands, program command/address/size, reset/start, poll completion, decode status and retry, copy read data, restore autodpcd, and release ownership.

## State, Persistence, Dependencies, And Integration
State includes channel index, aux interrupt mask, temporary xbuf, and GM200 control/status registers. Dependencies are auxch.h, nvkm MMIO, and GM200 pad/autodpcd hooks. Integration points are gm200_i2c pad constructors and DP AUX users on Maxwell-era display hardware.

## Risks And Test Signals
Risks: uses 8 native aux channels in gm200.c but one-bit interrupt per ch; timeout handling must leave hardware in a usable state; GSP-RM path disables native GM200 I2C. Test signals include DP AUX on GM200 without GSP-RM, address-only transactions, and clean failure on absent sinks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/auxgm200.c -->
