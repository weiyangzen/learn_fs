<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/auxch.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/auxch.c

## Purpose
Provides the common nvkm_i2c_aux object lifecycle and Linux i2c_adapter bridge for DisplayPort AUX channels, including acquisition, release, monitor mode, and I2C-over-AUX transfer splitting.

## Important APIs, Types, And Functions
Important APIs include nvkm_i2c_aux_i2c_xfer, nvkm_i2c_aux_monitor, nvkm_i2c_aux_acquire/release, nvkm_i2c_aux_xfer, nvkm_i2c_aux_lnk_ctl, nvkm_i2c_aux_ctor/new_/del/init/fini, and the nvkm_i2c_aux_i2c_algo.

## Control Flow
I2C-over-AUX transfers acquire the AUX pad, split messages into <=16 byte chunks, sets read/write and MOT bits, retries zero-length completions up to 32 times, and returns the original message count on success. Lifecycle functions toggle enabled under a mutex, register/unregister i2c_adapter objects, and delegate hardware transactions to aux->func.

## State, Persistence, Dependencies, And Integration
State includes aux enabled flag, mutex, pad pointer, id, interrupt mask bit, and registered i2c_adapter. Dependencies are Linux I2C core, pad arbitration, and generation-specific AUX xfer functions. Integration points are DP EDID over AUX, DPCD access, hotplug events, and external encoder AUX implementations.

## Risks And Test Signals
Risks: address-only transactions are rejected unless the backend advertises support; chunk retry handling relies on backend updating cnt; pad arbitration can return -EBUSY. Test signals include DP EDID reads over AUX I2C, direct AUX DPCD reads/writes, monitor mode switching, hotplug interrupt delivery, and suspend/resume init/fini.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/auxch.c -->
