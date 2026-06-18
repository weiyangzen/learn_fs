<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/auxch.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/auxch.h

## Purpose
Declares the internal AUX backend interface, constructors, generation-specific AUX constructors, transfer helper, link-control hook, autodpcd wrapper, and logging macros.

## Important APIs, Types, And Functions
Important type is nvkm_i2c_aux_func with address_only, xfer, and lnk_ctl. Important declarations include nvkm_i2c_aux_ctor/new_/del/init/fini/xfer, g94_i2c_aux_new/_xfer, gf119_i2c_aux_new, gm200_i2c_aux_new, and AUX_* macros.

## Control Flow
No executable control flow except inline nvkm_i2c_aux_autodpcd, which calls the i2c function hook when present. The inline currently passes false to the hook regardless of enable, so users should inspect whether this is intentional for disabling HW DPCD around manual AUX transactions.

## State, Persistence, Dependencies, And Integration
State is API contract only. Dependencies are pad.h and priv.h. Integration points are auxch.c, auxg94.c, auxgf119.c, auxgm200.c, anx9805.c, and generation i2c constructors.

## Risks And Test Signals
Risks: backend xfer signatures must honor size in/out semantics; the autodpcd helper's enable argument is not forwarded and is a review hotspot. Test signals include compile coverage of all backends and functional AUX transactions on generations with/without autodpcd hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/i2c/auxch.h -->
