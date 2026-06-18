# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_prime.c

Purpose: Provides vmwgfx PRIME/dma-buf handle conversion glue. Full dma-buf attach/map support is intentionally unimplemented for external virtual-device use, but fd-to-handle and handle-to-fd paths bridge TTM and GEM PRIME behavior.

Important APIs/types/functions: `vmw_prime_dmabuf_ops` supplies attach/detach/map/unmap/release ops; attach and map return `-ENOSYS`, detach/unmap are no-ops, and release is NULL. `vmw_prime_fd_to_handle()` first tries `ttm_prime_fd_to_handle()` and falls back to `drm_gem_prime_fd_to_handle()`. `vmw_prime_handle_to_fd()` decides whether to export via TTM or GEM based on handle range, dumb-BO state, and whether a surface handle aliases the BO.

Control flow: fd import is simple fallback. Export checks handles above `VMWGFX_NUM_MOB` as TTM object handles. For lower handles, it looks up the BO; dumb BOs export through GEM PRIME, non-dumb BOs try to locate a surface handle for the buffer and export that through TTM, otherwise fall back to GEM PRIME for the BO handle.

State and persistence: The file does not own long-lived state. It temporarily references BOs during lookup and releases them before returning. Exported dma-buf lifetime is owned by DRM/TTM/GEM infrastructure.

Dependencies and integration points: Depends on `ttm_object`, dma-buf ops, vmwgfx BO lookup, surface lookup by buffer, and DRM GEM PRIME fallback. Risks include limited dma-buf interoperability because attach/map are not implemented, handle namespace assumptions around `VMWGFX_NUM_MOB`, and correct BO unref on all paths. Test signals: PRIME import/export of dumb BOs, export of surface-backed buffers, invalid handle errors, fallback paths, and external device attach attempts returning `-ENOSYS`.
