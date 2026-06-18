<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/dma/priv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/dma/priv.h

## Purpose

`dma/priv.h` defines private DMA engine and DMA object function-table contracts.

## Important APIs, Types, And Functions

`nvkm_dma(p)` converts an engine pointer to `struct nvkm_dma`. `struct nvkm_dmaobj_func` currently contains the `bind()` callback used to materialize a DMA object into a GPU object under a parent. `struct nvkm_dma_func` contains `class_new()`, the generation-specific NVIF constructor. `nvkm_dma_new_()` is declared for generation selectors.

## Control Flow

Generation constructors create the engine with an `nvkm_dma_func`. User object constructors create `nvkm_dmaobj` instances with an `nvkm_dmaobj_func`. Later object binding routes through `dmaobj->func->bind()`.

## State And Persistence Behavior

This header does not store state, but it defines the function pointers persisted in `struct nvkm_dma` and `struct nvkm_dmaobj`.

## Dependencies And Integration Points

It includes public `engine/dma.h` and is used by `base.c`, generation selectors, and user DMA object encoders.

## Risks And Edge Cases

The bind contract must return a GPU object whose layout matches the target generation and parent alignment requirements. Future fields must preserve all existing constructor call sites.

## Test Signals

Build coverage across all DMA files and successful bind callbacks during FIFO channel construction validate the contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/dma/priv.h -->
