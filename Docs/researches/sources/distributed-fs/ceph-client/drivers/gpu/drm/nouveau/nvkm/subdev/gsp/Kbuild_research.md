<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/Kbuild -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/Kbuild

## Purpose
Builds GSP subdevice support and generation-specific GSP implementations.

## Important APIs, Types, And Functions
Adds `base.o`, `fwsec.o`, generation files from GV100 through GB202, and includes the `rm/` subdirectory.

## Control Flow
Kbuild controls object inclusion for firmware loading, FWSEC boot, and RM-backed GSP support.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
Connects GSP core, FWSEC, generation constructors, and RM implementation objects.

## Risks And Edge Cases
Missing objects can break firmware interface discovery or RM support for a generation.

## Test Signals
Kernel build success and available constructors for listed GPU generations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/Kbuild -->
