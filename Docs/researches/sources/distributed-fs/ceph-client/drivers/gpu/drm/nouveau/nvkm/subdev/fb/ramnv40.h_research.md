<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ramnv40.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ramnv40.h

## Purpose
Private header for NV40-style RAM reclocking state and constructor sharing.

## Important APIs, Types, And Functions
Defines `struct nv40_ram`, embedding `struct nvkm_ram` plus cached `ctrl` and `coef` PLL programming values. Declares `nv40_ram_new_()`.

## Control Flow
No runtime flow. NV41/NV44/NV49 wrappers call the shared constructor after detecting type/size.

## State And Persistence
The `ctrl` and `coef` fields persist between `calc` and `prog` and drive hardware PLL writes in `ramnv40.c`.

## Dependencies And Integration Points
Includes `ram.h` and is used by NV40-family RAM files.

## Risks
All users share the same PLL-state layout; constructor callers must pass correct type and size from generation-specific detection.

## Test Signals
Build coverage and successful NV4x RAM construction/reclocking validate the header contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ramnv40.h -->
