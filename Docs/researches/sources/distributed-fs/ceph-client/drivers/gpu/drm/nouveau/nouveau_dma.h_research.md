# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_dma.h

Purpose: Declares the DMA push-ring helper API, constants, object handles, and inline macros used by Nouveau channel submission and generation-specific push emitters.

Important APIs/macros: `nouveau_dma_wait()`, `NOUVEAU_DMA_SKIPS`, `NV50_DMA_PUSH_MAX_LENGTH`, `NV50_DMA_IB_MAX`, object handles such as `NvDmaFB`, `NvDmaTT`, `NvNotify0`, `NvSema`, `NvEvoSema0/1`, `RING_SPACE()`, `OUT_RING()`, `WRITE_PUT()`, `FIRE_RING()`, and `WIND_RING()`. It also defines NV_SW method offsets for vblank semaphore/page-flip operations.

Control flow/state contract: Push emitters call `RING_SPACE()` before writing commands with `OUT_RING()` or nvif push helpers. `FIRE_RING()` writes hardware PUT if new commands were emitted and advances the stored PUT cursor; `WIND_RING()` discards unsubmitted commands by resetting `cur` to `put`. `WRITE_PUT()` uses a memory barrier and a readback before the nvif PUT write.

Dependencies/integration: Includes `nouveau_bo.h` and `nouveau_chan.h`. Uses BO-backed push buffer access and nvif user register writes. Generation-specific BO copy files and old display/fence paths depend on these constants.

Risks/test signals: Incorrect space accounting or PUT writes can hang command submission. Consumers must reserve enough space before raw writes. Test through pushbuf wrap stress, fence/page-flip semaphore paths, copy engine push emission, and architectures requiring strict memory ordering.
