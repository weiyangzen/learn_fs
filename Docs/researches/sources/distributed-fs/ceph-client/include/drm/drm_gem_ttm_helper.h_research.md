# sources/distributed-fs/ceph-client/include/drm/drm_gem_ttm_helper.h

Purpose: Declares adapter helpers that let TTM buffer objects participate in GEM object callbacks for printing, vmap/vunmap, mmap, and dumb-buffer map-offset handling.

Important APIs, types, and functions: Defines `drm_gem_ttm_of_gem()` and declares `drm_gem_ttm_print_info()`, `drm_gem_ttm_vmap()`, `drm_gem_ttm_vunmap()`, `drm_gem_ttm_mmap()`, and `drm_gem_ttm_dumb_map_offset()`.

Control flow: TTM-backed drivers use the container macro to recover `struct ttm_buffer_object` from the embedded GEM base, install helper callbacks in GEM object funcs or driver dumb-map ops, and route userspace mmap/map-offset requests through TTM's BO mapping logic.

State and persistence: No independent state is stored. Helpers operate on TTM BO state embedded around the GEM base and on transient virtual mappings.

Dependencies and integration points: Depends on DRM device/GEM and TTM BO headers. Integrated by VRAM helpers and TTM-based drivers that expose GEM APIs.

Risks and test signals: Risks include wrong container assumptions for non-TTM GEM objects, BO reservation/pinning mistakes during vmap/mmap, and offset exposure for evictable BOs. Test TTM GEM mmap, vmap/vunmap, dumb map offset, eviction around mappings, and debug info printing.
