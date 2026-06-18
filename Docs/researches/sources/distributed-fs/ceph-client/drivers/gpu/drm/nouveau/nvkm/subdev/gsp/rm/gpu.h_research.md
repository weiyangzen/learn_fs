<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/gpu.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/gpu.h

## Purpose
Declares the RM GPU class metadata structure used by GSP-RM constructors.

## Important APIs, Types, And Functions
Defines `struct nvkm_rm_gpu` with display, usermode, FIFO, CE, GR, NVDEC, NVENC, NVJPG, and OFA class/callback fields. Declares external tables for TU1xx, GA100, GA1xx, AD10x, GH100, GB10x, and GB20x.

## Control Flow
No runtime flow. The selected GSP firmware function table points `gsp->rm->gpu` to one of these tables.

## State And Persistence
The selected table persists in `struct nvkm_rm` and drives object allocation throughout device lifetime.

## Dependencies And Integration Points
Included by RM engine/display/FIFO code and generation class table files.

## Risks And Edge Cases
Zero class fields indicate unavailable functionality only if callers handle them. Incorrect callbacks or class IDs break RM allocations.

## Test Signals
Correct class exposure and successful RM object construction across all table users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/gpu.h -->
