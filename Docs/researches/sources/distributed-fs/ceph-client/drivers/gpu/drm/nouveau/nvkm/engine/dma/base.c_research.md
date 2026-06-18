<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/dma/base.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/dma/base.c

## Purpose

`dma/base.c` implements the generic DMA object engine wrapper. It exposes NVIF DMA classes, forwards object construction to generation-specific encoders, and creates the engine.

## Important APIs, Types, And Functions

`nvkm_dma_oclass_new()` calls `dma->func->class_new()` and returns the embedded `nvkm_dmaobj` object. `nvkm_dma_sclass[]` exposes `NV_DMA_FROM_MEMORY`, `NV_DMA_TO_MEMORY`, and `NV_DMA_IN_MEMORY`. `nvkm_dma_oclass_base_get()` enumerates base-device classes, while `nvkm_dma_oclass_fifo_get()` enumerates FIFO child classes. `nvkm_dma_new_()` allocates `struct nvkm_dma`, stores the generation function table, and calls `nvkm_engine_ctor()`.

## Control Flow

Probe selects a generation constructor, which calls `nvkm_dma_new_()`. User/FIFO class enumeration returns DMA classes. A create request reaches `nvkm_dma_oclass_new()`, which invokes the generation `class_new` function to parse arguments and build a DMA object.

## State And Persistence Behavior

Persistent state is the `struct nvkm_dma` engine and its `func` pointer. Individual DMA object state is allocated in the user implementation files and persists as NVKM objects until destroyed.

## Dependencies And Integration Points

It depends on generic engine/object infrastructure, NVIF class IDs, and FIFO integration because DMA objects are commonly bound into channel RAMHT/RAMFC state.

## Risks And Edge Cases

The class arrays are ABI-visible; removing or reordering classes can break clients. `class_new` must set `*pobject` only when an object was successfully allocated enough to return. Enumeration functions return count when index is exhausted.

## Test Signals

Signals include class enumeration showing three DMA classes, successful DMA object creation through base and FIFO paths, and build/link coverage for every generation `class_new` function.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/dma/base.c -->
