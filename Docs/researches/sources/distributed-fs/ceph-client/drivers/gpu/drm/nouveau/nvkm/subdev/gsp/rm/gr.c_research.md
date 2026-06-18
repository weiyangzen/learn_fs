<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/gr.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/gr.c

## Purpose
Creates the RM-backed graphics engine wrapper and routes graphics class object construction through RM allocations.

## Important APIs, Types, And Functions
Defines `nvkm_rm_gr_new`, `nvkm_rm_gr_obj_ctor`, `nvkm_rm_gr_init`, and `nvkm_rm_gr_fini`.

## Control Flow
`nvkm_rm_gr_new` builds an `nvkm_gr_func` with I2M, 2D, 3D, and compute classes from `rm->gpu->gr.class`, sets R535 GR hooks for oneinit, units, and channel creation, allocates `struct r535_gr`, and installs it as `device->gr`. Init/fini optionally call RM API scrubber hooks.

## State And Persistence
Persists the graphics engine object, its function table, R535 context buffer metadata, and scrubber channel state.

## Dependencies And Integration Points
Depends on `r535_gr_*` functions, RM GPU class tables, NVKM GR engine framework, FIFO channels, and RM object allocation helpers.

## Risks And Edge Cases
Class table entries must be valid. Scrubber hooks are optional. GR context buffer metadata is populated in R535 oneinit and must match RM expectations.

## Test Signals
Successful GR engine creation, graphics/compute object allocation, context promotion, and scrubber init/fini if present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/gr.c -->
