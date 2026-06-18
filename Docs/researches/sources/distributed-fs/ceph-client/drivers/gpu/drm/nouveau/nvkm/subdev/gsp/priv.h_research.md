<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/priv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/priv.h

## Purpose
Declares the private GSP firmware-interface and function-table contracts shared by GSP base, generation files, FWSEC, and RM code.

## Important APIs, Types, And Functions
Declares FWSEC APIs, `struct nvkm_gsp_fwif`, firmware load helpers, firmware declaration macros, `struct nvkm_gsp_func`, generation hooks for TU102/GA102/GH100/R535, and `nvkm_gsp_new_`.

## Control Flow
No runtime flow. It defines how firmware interface arrays select loaders, function tables, RM implementations, and version strings.

## State And Persistence
Function tables and selected firmware interface metadata persist in each GSP object. Firmware declaration macros affect module firmware metadata.

## Dependencies And Integration Points
Includes public `subdev/gsp.h` and RM GPU definitions; links generation code with common GSP and R535 lifecycle helpers.

## Risks And Edge Cases
The table contract is broad and mostly convention-based. Missing hooks must be handled by callers or will lead to null calls in generation paths.

## Test Signals
Compile/link success, firmware interface selection, and correct lifecycle dispatch for all generations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/priv.h -->
