<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/engine.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/engine.h

## Purpose
Declares the shared RM-backed engine constructor interface.

## Important APIs, Types, And Functions
Declares `nvkm_rm_engine_ctor`, `nvkm_rm_engine_new`, `nvkm_rm_engine_obj_new`, `nvkm_rm_gr_new`, `nvkm_rm_nvdec_new`, and `nvkm_rm_nvenc_new`.

## Control Flow
No runtime flow. It exposes constructors to common RM, GR, and video engine files.

## State And Persistence
No state is stored here.

## Dependencies And Integration Points
Includes `gpu.h` and links generic engine construction with GR/video wrappers.

## Risks And Edge Cases
The declarations assume callers pass valid RM, class, and instance data. Implementation enforces most runtime checks.

## Test Signals
Compile/link success and correct use by RM engine files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/engine.h -->
