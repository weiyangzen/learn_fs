<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fuse/Kbuild -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fuse/Kbuild

## Purpose
Builds the fuse subdevice implementations.

## Important APIs, Types, And Functions
Adds `base.o`, `nv50.o`, `gf100.o`, and `gm107.o` to `nvkm-y`.

## Control Flow
Kbuild compiles the common fuse layer and generation-specific readers into NVKM.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
Connects the public fuse subsystem with NV50, GF100, and GM107 reader implementations.

## Risks And Edge Cases
Missing objects break constructor availability or link coverage for supported chipsets.

## Test Signals
Build success and successful fuse subdevice construction on supported hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fuse/Kbuild -->
