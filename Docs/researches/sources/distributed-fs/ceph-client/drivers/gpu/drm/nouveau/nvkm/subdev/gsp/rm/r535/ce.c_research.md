<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/ce.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/ce.c

## Purpose
Allocates R535 RM copy-engine objects.

## Important APIs, Types, And Functions
Defines `r535_ce_alloc` and exports `r535_ce` as an `nvkm_rm_api_engine`.

## Control Flow
Allocation obtains CE parameters from `nvkm_gsp_rm_alloc_get`, sets version 1 and `engineType` to `NV2080_ENGINE_TYPE_COPY0 + inst`, then writes the allocation RPC.

## State And Persistence
The created RM CE object persists through the supplied `nvkm_gsp_object`.

## Dependencies And Integration Points
Called by generic RM engine object construction for CE classes.

## Risks And Edge Cases
Instance-to-engineType mapping assumes contiguous RM copy engine IDs. Allocation parameter retrieval can fail.

## Test Signals
Successful CE object allocation for each exposed copy engine instance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/ce.c -->
