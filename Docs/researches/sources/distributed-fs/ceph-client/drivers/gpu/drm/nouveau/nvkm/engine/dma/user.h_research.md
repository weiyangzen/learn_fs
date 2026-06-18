<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/dma/user.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/dma/user.h

## Purpose

`dma/user.h` declares the shared DMA object constructor and all generation-specific DMA object constructors.

## Important APIs, Types, And Functions

`nvkm_dmaobj(p)` converts an NVKM object to `struct nvkm_dmaobj`. `nvkm_dmaobj_ctor()` performs generic parsing/normalization. `nv04_dmaobj_new()`, `nv50_dmaobj_new()`, `gf100_dmaobj_new()`, `gf119_dmaobj_new()`, and `gv100_dmaobj_new()` are the generation constructors selected by generation files.

## Control Flow

Generic DMA class creation calls a generation `class_new`, which is one of these declared constructors. Each generation constructor calls the shared constructor before adding layout-specific flags and bind behavior.

## State And Persistence Behavior

No state is stored in the header. It declares how generic and generation object state is initialized.

## Dependencies And Integration Points

It includes `priv.h` and is consumed by `base.c`, all generation selector files, and all user object encoders.

## Risks And Edge Cases

Prototype drift would break all generation constructors. The shared constructor mutates the data pointer and size, so generation-specific parsers must use the updated values.

## Test Signals

Build success across all DMA generations and successful parsing of both generic and generation-specific DMA create arguments validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/dma/user.h -->
