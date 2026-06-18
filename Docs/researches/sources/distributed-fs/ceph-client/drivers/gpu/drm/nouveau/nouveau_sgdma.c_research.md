# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_sgdma.c

## Purpose
This file implements Nouveau's scatter-gather TTM translation-table backend for system/GART memory. It allocates `ttm_tt` state, binds host pages into Nouveau memory objects, maps pre-Tesla GART mappings, and tears the mapping down.

## Important APIs, Types, and Functions
`struct nouveau_sgdma_be` embeds `struct ttm_tt` first for compatibility with Nouveau BO population paths and stores the active `struct nouveau_mem`. Public functions are `nouveau_sgdma_create_ttm`, `nouveau_sgdma_bind`, `nouveau_sgdma_unbind`, and `nouveau_sgdma_destroy`.

## Control Flow
Creation chooses TTM caching from BO coherency, AGP bridge presence, and normal cached memory, then calls `ttm_sg_tt_init`. Bind is idempotent if `nvbe->mem` already exists, converts the TTM pages into a host `nouveau_mem`, and for pre-Tesla non-AGP style mappings maps it into the client VMM. Unbind finalizes the memory object and clears the pointer. Destroy finalizes the embedded TTM object and frees the backend.

## State and Persistence Behavior
The backend persists only while a TTM BO has a translation table. Binding state is represented by `nvbe->mem`; unbind removes GPU-visible mappings and host memory descriptors.

## Dependencies and Integration Points
It integrates with TTM TT allocation, Nouveau BO resource placement, `nouveau_mem_host`, `nouveau_mem_map`, and `nouveau_mem_fini`. It is declared through `nouveau_ttm.h` and used by the Nouveau BO driver.

## Risks
The first-field layout requirement is fragile. Caching selection affects CPU/GPU coherency, especially forced coherent and AGP paths. Failure after pre-Tesla mapping must call `nouveau_mem_fini` to avoid stale VMM state.

## Test Signals
Signals include GART BO creation, bind/unbind under eviction, AGP and non-AGP pre-Tesla paths, coherent GART CPU/GPU readback, and memory pressure during TTM population.
