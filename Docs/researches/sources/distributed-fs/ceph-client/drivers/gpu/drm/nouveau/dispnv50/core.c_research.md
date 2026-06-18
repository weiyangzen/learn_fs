<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/core.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/core.c

## Purpose
This file selects, creates, and destroys the NV50 display core DMA channel implementation for the detected display hardware class.

## Important APIs, Types, and Functions
Public functions are `nv50_core_new` and `nv50_core_del`. The class table maps NV50 through Blackwell-era core channel classes to constructors such as `core507d_new`, `core827d_new`, `core907d_new`, `core917d_new`, `corec37d_new`, `corec57d_new`, and `coreca7d_new`.

## Control Flow
`nv50_core_new` asks `nvif_mclass` to choose the first supported class from the ordered table and dispatches to the matching constructor. If no class is supported, it logs and returns the error. `nv50_core_del` destroys the DMA channel, frees the core object, and nulls the caller pointer.

## State and Persistence Behavior
The file owns no long-term state beyond creating/freeing `struct nv50_core`; constructors initialize the function table, display pointer, and channel. Deletion tears down channel state through `nv50_dmac_destroy`.

## Dependencies and Integration Points
It depends on `nv50_disp(drm->dev)->disp->object`, NVIF class matching, and constructor declarations in `core.h`. The selected core function table drives heads, outputs, CRC, caps, window ownership, and update behavior.

## Risks
Class-table order controls preferred implementation. Missing or wrong class mappings can prevent display init on whole GPU generations. Teardown assumes the core pointer is either fully initialized enough for `nv50_dmac_destroy` or NULL.

## Test Signals
Display init across supported GPU generations, forced unsupported-class failure, suspend/unload teardown, and core channel update/caps initialization after selection validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/core.c -->
