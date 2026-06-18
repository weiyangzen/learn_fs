# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pci/agp.h

## Purpose
Declares AGP helper functions or provides no-op stubs when AGP support is unavailable.

## Important APIs, Types, And Functions
Declares/stubs `nvkm_agp_ctor`, `nvkm_agp_dtor`, `nvkm_agp_preinit`, `nvkm_agp_init`, and `nvkm_agp_fini`.

## Control Flow
Conditional compilation selects real declarations for `CONFIG_AGP` or AGP module builds, otherwise inline no-ops and `-ENOSYS` init.

## State And Persistence
No direct state is stored. It controls whether PCI base can call real AGP lifecycle functions.

## Dependencies And Integration Points
Includes `priv.h` and is consumed by `base.c` and `agp.c`.

## Risks And Test Signals
Risk is configuration mismatch between AGP objects and header stubs. Test AGP built-in, AGP module, and no-AGP configurations.
