# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bar/priv.h

## Purpose
Defines BAR private function-table contracts and shared helper prototypes.

## Important APIs, types, and functions
`struct nvkm_bar_func` provides destructor, oneinit, optional init, BAR1/BAR2 init/fini/wait/VMM hooks, and flush. The header declares `nvkm_bar_ctor()`, R535 constructor, NV50/GF100 fini helpers, G84 flush, and GM107 wait helpers.

## Control flow, state, and persistence
No code runs here. The function table drives BAR base lifecycle and public BAR helper behavior.

## Dependencies and integration points
Includes public `subdev/bar.h`. Used by all BAR generation files and BAR base.

## Risks and test signals
Missing hooks alter public behavior, especially BAR2 initialization. Build coverage plus BAR1/BAR2 reset/init tests validate table completeness.
