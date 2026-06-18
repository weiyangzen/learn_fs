# sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/ttm_bo_util.c

Purpose: utility layer for BO memory IO reservation, CPU mappings, memcpy and accelerated move cleanup, ghost BOs, pipeline gutting, LRU walks, and shrink helpers.

Important APIs and functions: exports `ttm_mem_io_reserve()`, `ttm_mem_io_free()`, `ttm_move_memcpy()`, `ttm_bo_move_memcpy()`, `ttm_io_prot()`, `ttm_bo_kmap_try_from_panic()`, `ttm_bo_kmap()`, `ttm_bo_kunmap()`, `ttm_bo_vmap()`, `ttm_bo_vunmap()`, `ttm_bo_move_accel_cleanup()`, `ttm_bo_move_sync_cleanup()`, `ttm_lru_walk_for_evict()`, `ttm_bo_lru_cursor_*()`, `ttm_bo_shrink()`, `ttm_bo_shrink_suitable()`, and `ttm_bo_shrink_avoid_wait()`.

Control flow: memcpy moves initialize TT or linear IO iterators for source and destination, populate swapped TT when needed, optionally clear instead of copying nonexistent data, then synchronously clean up old resources. Accelerated moves attach a fence and either move old memory to a ghost BO, remember a pipelined eviction fence, or wait and free. Pipeline gutting purges content, creating an unpopulated clearing TT or ghosting old contents if fences are active. LRU cursors combine resource-cursor iteration, trylock/ticket-lock reservation, ref acquisition, and validation that the BO still owns the same memory type.

State and dependencies: manages resource bus mappings, kmap/vmap/ioremap state, ghost BO krefs, DMA fences, TT population, bulk move, LRU cursor state, and backup/shrink flags. It depends on TTM resource/kmap iterators, DMA-resv, DRM cache helpers, VM mapping APIs, and `ttm_tt_backup()`.

Risks and test signals: TODOs note direct member copy in ghost BOs and eviction fence slot limits. High-risk areas are IO map cleanup symmetry, encrypted/decrypted page protections, ghost ownership of TT/resource, and LRU walk lock ordering.
