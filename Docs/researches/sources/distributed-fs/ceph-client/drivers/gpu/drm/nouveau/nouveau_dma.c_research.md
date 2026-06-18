# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_dma.c

Purpose: Implements legacy DMA push-ring space management for Nouveau channels. It waits for free push-buffer space, handles GET pointer validation, detects timeouts, and wraps the ring through the skip area.

Important APIs/functions: `nouveau_dma_wait()` is the exported wait/space function used by `RING_SPACE()` and channel push callbacks. Internal `READ_GET()` reads the GPU GET pointer from USERD/user object, resets timeout progress when GET advances, detects lockup after repeated stalled reads, validates that GET is inside the main push buffer, and returns an adjusted dword offset.

Control flow: `nouveau_dma_wait()` loops until `chan->dma.free >= size`. If GET is invalid or in the skip area, it keeps polling. When GET is behind or equal to the current PUT, it uses space to the ring end; if insufficient, it emits a jump back to the start, waits until GET leaves the skip region, writes PUT to `NOUVEAU_DMA_SKIPS`, and resets ring cursors. When GET is ahead, it computes free space as `get - cur - 1`.

State/persistence: Mutates `chan->dma.free`, `cur`, and `put`, writes jump commands into the push BO, and updates hardware PUT through macros in `nouveau_dma.h`.

Dependencies/integration: Depends on channel USERD offsets, push buffer address, BO read/write helpers, nvif user register access, and memory barriers from `WRITE_PUT()`. Used by all legacy push submission paths and class-specific BO move push emission.

Risks/test signals: GET pointer races can cause ring corruption or false GPU lockups. The skip-area race workaround is subtle and generation-sensitive. Test with small ring wrap cases, indirect push buffers that temporarily move GET outside the main ring, stalled GPU timeout behavior, and stress command submission under concurrent fences.
