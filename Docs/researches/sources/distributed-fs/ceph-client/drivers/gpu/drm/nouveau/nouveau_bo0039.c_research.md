# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_bo0039.c

Purpose: Provides NV04-era M2MF buffer copy support for Nouveau BO migration through the `NV039` class.

Important APIs/functions: `nv04_bo_move_m2mf()` emits pushbuf methods for page-sized copies between old and new TTM resources. `nv04_bo_move_init()` binds the M2MF object and notification context. The helper `nouveau_bo_mem_ctxdma()` selects `NvDmaTT` for TT memory or the channel VRAM context handle otherwise.

Control flow: The move function programs source/destination context DMA, then loops over the resource size in batches of at most 2047 pages. For each batch it writes offsets, pitches, line length/count, format, buffer notify, and a no-op launch. Offsets advance by copied page count.

State/persistence: No persistent file-local state. It consumes channel push state, context DMA handles, and TTM resource start/size.

Dependencies/integration: Called from `nouveau_bo_move_init()`'s method table when class `0x0039` is available. Depends on `nouveau_dma.h`, `nvif/push006c.h`, and class register definitions from `cl0039.h`.

Risks/test signals: Risks are incorrect context DMA selection, page count batching, or offset truncation on old hardware. Tests are BO migration between VRAM/GART/system on NV04-NV4x hardware, pushbuf wait failure injection, and checking `MM: using M2MF for buffer copies` logs.
