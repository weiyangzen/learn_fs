<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/dma/user.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/dma/user.c

## Purpose

`dma/user.c` implements generic NVIF DMA object parsing, object lifetime, search, and bind dispatch shared by all generation encoders.

## Important APIs, Types, And Functions

`nvkm_dmaobj_search()` looks up a client object by handle and verifies it uses the DMA object function table. `nvkm_dmaobj_bind()` dispatches to the generation `bind` callback. `nvkm_dmaobj_dtor()` returns the embedded object for freeing. `nvkm_dmaobj_ctor()` constructs the object, unpacks `nv_dma_v0`, stores target/access/start/limit, validates range ordering, and maps NVIF target/access enums to internal `NV_MEM_TARGET_*` and `NV_MEM_ACCESS_*`.

## Control Flow

A generation `*_dmaobj_new()` allocates its extended object, calls `nvkm_dmaobj_ctor()`, then parses any generation-specific tail arguments and computes descriptor flags. Later FIFO/channel code searches or binds the object through the generic function table.

## State And Persistence Behavior

The generic fields persisted in `struct nvkm_dmaobj` are `func`, `dma`, `target`, `access`, `start`, and `limit`. Generation files add descriptor-specific fields.

## Dependencies And Integration Points

It depends on NVIF class `cl0002`, unpack helpers, client object lookup, GPU object binding, and framebuffer memory target definitions.

## Risks And Edge Cases

The constructor rejects inverted ranges and unknown target/access values. `NV_DMA_V0_TARGET_VM` and `NV_DMA_V0_ACCESS_VM` are only meaningful for generations that support VM-style objects. Returning partially allocated objects on constructor failure must be cleaned by callers through normal object lifetime.

## Test Signals

Signals include ioctl traces for DMA creation, rejection of bad ranges/enums, successful handle lookup, and generation bind callbacks receiving normalized target/access values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/dma/user.c -->
