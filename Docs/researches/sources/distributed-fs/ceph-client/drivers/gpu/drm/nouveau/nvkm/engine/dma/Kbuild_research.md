<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/dma/Kbuild -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/dma/Kbuild

## Purpose

`dma/Kbuild` lists the nouveau DMA object engine sources built into `nvkm-y`.

## Important APIs, Types, And Functions

It includes the generic engine (`base.o`), generation selectors (`nv04.o`, `nv50.o`, `gf100.o`, `gf119.o`, `gv100.o`), and user DMA object implementations (`user.o`, `usernv04.o`, `usernv50.o`, `usergf100.o`, `usergf119.o`, `usergv100.o`).

## Control Flow

There is no runtime control flow. Kernel build logic includes these objects so chipset constructors and NVIF DMA object classes are linked.

## State And Persistence Behavior

No runtime state is stored. The file controls compilation coverage and therefore which constructors can be referenced by the device table.

## Dependencies And Integration Points

It integrates with the parent nouveau Kbuild and the `nvkm-y` aggregate object list.

## Risks And Edge Cases

Missing one of these objects would cause link failures or unsupported DMA object creation for a GPU generation. Adding a new generation requires both implementation and Kbuild inclusion.

## Test Signals

Build success with all DMA constructors linked is the primary signal. Runtime signals are successful creation of NV_DMA_* classes across supported generations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/dma/Kbuild -->
