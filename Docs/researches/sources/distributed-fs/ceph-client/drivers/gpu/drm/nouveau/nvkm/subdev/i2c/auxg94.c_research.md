<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/auxg94.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/auxg94.c

## Purpose
Implements DP AUX transfers for G94-style hardware using MMIO blocks at 0x00e4c0/0x00e4d0/0x00e4e0/0x00e4e4/0x00e4e8 plus pad ownership handshakes.

## Important APIs, Types, And Functions
Important functions are g94_i2c_aux_init/fini, g94_i2c_aux_xfer, g94_i2c_aux_new_, g94_i2c_aux_new, and g94_i2c_aux_func.

## Control Flow
Transfer init waits for idle, requests AUX ownership with magic bits, checks sink detect, disables autodpcd, writes up to 16 bytes for writes, programs type/size/address, resets and starts the transaction, polls up to 2 ms, decodes retry/timeout/error status, optionally retries up to 32 times, reads data/status for reads, re-enables autodpcd, and releases ownership.

## State, Persistence, Dependencies, And Integration
State includes channel number, aux interrupt bit, temporary transfer buffer, and hardware control/status registers. Dependencies are auxch.h, nvkm MMIO helpers, pad->i2c, and optional aux_autodpcd hook. Integration points are g94/gf119 pad constructors and DP AUX/DPCD/EDID logic.

## Risks And Test Signals
Risks: fixed register offsets and bit meanings are generation-specific; sink-not-detected is returned as -ENXIO; retry/status code mapping must match hardware. Test signals include DPCD reads/writes, hotplug detect, AUX retry behavior, and no stuck ownership after timeout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/auxg94.c -->
