# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_chan.c

Purpose: Creates, initializes, idles, kills, and destroys Nouveau command channels. It allocates push buffers, context DMA objects, USERD memory, semaphore BOs, kill events, legacy SW fence objects, and runlist/channel accounting used by fences, GEM command submission, and BO migration.

Important APIs/functions: `nouveau_channel_new()`, `nouveau_channel_del()`, `nouveau_channel_idle()`, `nouveau_channel_kill()`, `nouveau_channels_init()`, and `nouveau_channels_fini()`. Internal construction is split into `nouveau_channel_prep()`, `nouveau_channel_ctor()`, `nouveau_channel_init()`, plus push callbacks `nouveau_channel_wait()` and `nouveau_channel_kick()`.

Control flow: Constructor selects the highest supported channel class, allocates a push BO in coherent GART or optional VRAM, maps it and possibly a GPU VMA, builds ctxdma for legacy classes, allocates USERD for Volta+, creates the nvif channel object, maps USERD, registers kill notification for Fermi+, creates VRAM/GART context DMA for pre-Fermi, initializes the nvif channel push backend for NV50/Fermi/Volta variants, reserves skip NOP space, creates legacy software fence object on old chips, creates a fence context, and joins SVM. Destruction reverses these resources and parts SVM if needed.

State/persistence: `struct nouveau_channel` keeps nvif channel/object handles, runlist/chid/inst/token, push BO/VMA/ctxdma/address, dma ring cursors, USERD offsets, semaphore BO/VMA, fence context pointer, kill event, and killed atomic flag. Driver-wide runlist metadata is allocated from nvif device info.

Dependencies/integration: Depends on nvif channel/object/event/mem APIs, BO/VMM/SVM/fence subsystems, DMA ring helpers, and module parameter `vram_pushbuf`. Used by GEM command submission, TTM copy engine setup, fences, and GPU reset/killed-channel handling.

Risks/test signals: Resource teardown must tolerate partially constructed channels. Push buffer address mode differs sharply by generation and memory domain. Kill events must poison fences to avoid hangs. Test channel create/destroy under failures, SVM join/part, fence idle behavior, vram_pushbuf mode, runlist accounting, and GPU reset/channel kill notification.
