# sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/ttm_agp_backend.c

Purpose: AGP backend implementation for TTM translation tables. It wraps `struct ttm_tt` with AGP allocation/bind state so drivers using AGP aperture memory can bind TT pages into an AGP bridge.

Important APIs and functions: exports `ttm_agp_bind()`, `ttm_agp_unbind()`, `ttm_agp_is_bound()`, `ttm_agp_destroy()`, and `ttm_agp_tt_create()`. `ttm_agp_tt_create()` allocates `struct ttm_agp_backend`, stores the bridge, initializes the embedded TT with write-combined caching, and returns the TT pointer. `ttm_agp_bind()` allocates AGP memory, fills it with TT pages or the global dummy read page for holes, sets cached or uncached AGP type, and binds at `bo_mem->start`. `ttm_agp_unbind()` unbinds if bound or frees AGP memory if only allocated. Destroy unbinds, finalizes TT, and frees the wrapper.

State and persistence: persistent runtime state is `agp_be->mem`, `agp_be->bridge`, TT page vector, caching mode, and global dummy page from `ttm_glob`. There is no durable storage.

Dependencies and integration: depends on Linux AGP backend APIs, `ttm_tt`, `ttm_resource`, and TTM global initialization. It integrates as a driver-provided TT create/bind backend for legacy AGP-capable DRM drivers.

Risks and test signals: binding uses dummy pages for missing TT entries and assumes `ttm_glob.dummy_read_page` exists. Error handling logs AGP bind failure but leaves `agp_be->mem` assigned. No local KUnit coverage in this subset directly exercises AGP behavior.
