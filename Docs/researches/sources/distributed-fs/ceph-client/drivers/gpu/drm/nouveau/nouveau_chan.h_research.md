# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_chan.h

Purpose: Declares the Nouveau channel object and lifecycle API used by command submission, fences, DMA push helpers, copy engines, and SVM.

Important APIs/types: `struct nouveau_channel` embeds `struct nvif_chan` and stores client/VMM references, USERD memory/object, runlist/channel identifiers, VRAM/GART/NVSW objects, push buffer BO/VMA/ctxdma/address, fence pointer, DMA ring cursor fields, USER GET/PUT offsets, semaphore BO/VMA, user/blit objects, kill event, and killed flag. Public functions are `nouveau_channels_init/fini()`, `nouveau_channel_new()`, `nouveau_channel_del()`, `nouveau_channel_idle()`, and `nouveau_channel_kill()`. The module parameter `nouveau_vram_pushbuf` is exported.

Control flow/state contract: Callers create a channel with runmask and context handles, submit through `chan.push` and DMA helpers, idle through a fence, and delete with a pointer-to-pointer API that nulls the caller's reference. Kill state is atomic and propagates to the fence context.

Dependencies/integration: Includes nvif object/event/channel headers and forward-declared device data. It is tightly coupled to `nouveau_dma.h` macros, `nouveau_fence`, BO/VMA allocation, and nvif channel constructors.

Risks/test signals: Consumers must not touch a channel after kill/delete, and ring cursor fields must remain consistent with push callback updates. Test signals include lockdep around channel mutex users, fence context teardown, channel kill events, runlist-aware channel counts, and compile coverage across legacy and GPFIFO channel paths.
