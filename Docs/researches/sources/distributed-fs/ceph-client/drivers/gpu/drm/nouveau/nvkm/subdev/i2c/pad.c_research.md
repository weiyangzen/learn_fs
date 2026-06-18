<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/pad.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/pad.c

## Purpose
Implements common pad arbitration, mode switching, construction/destruction, and init/fini for physical pins shared by I2C and AUX users.

## Important APIs, Types, And Functions
Important APIs are nvkm_i2c_pad_mode, nvkm_i2c_pad_acquire/release, nvkm_i2c_pad_init/fini/del/ctor/new_, and internal nvkm_i2c_pad_mode_locked.

## Control Flow
Acquire locks the pad mutex and either accepts the current mode, switches from OFF to requested I2C/AUX mode, or returns -EBUSY if another mode owns the pad. Release unlocks and may call mode_locked for OFF state. Init reapplies stored mode; fini forces OFF.

## State, Persistence, Dependencies, And Integration
State includes pad mode, mutex, id, list link, i2c pointer, and backend mode hook. Dependencies are pad.h and generation-specific mode functions. Integration points are bus and aux acquire/release paths.

## Risks And Test Signals
Risks: pad_release appears to call mode_locked only when mode is OFF, so active mode may remain selected until explicit mode/fini; contention bugs surface as -EBUSY. Test signals include concurrent I2C/AUX access rejection and correct mode register programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/pad.c -->
