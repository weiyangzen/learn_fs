# sources/distributed-fs/ceph-client/drivers/gpu/drm/qxl/qxl_object.c

Purpose: This file implements QXL BO creation, placement selection, mapping, pinning, reference management, surface-ID checks, and full VRAM/surface eviction helpers.

Important APIs, types, and functions: `qxl_bo_create()`, `qxl_ttm_placement_from_domain()`, `qxl_bo_pin()/unpin()`, `qxl_bo_pin_locked()/unpin_locked()`, `qxl_bo_pin_and_vmap()`, `qxl_bo_vmap_locked()`, `qxl_bo_vunmap_locked()`, `qxl_bo_kmap_atomic_page()`, `qxl_bo_kunmap_atomic_page()`, `qxl_bo_ref()/unref()`, `qxl_bo_check_id()`, `qxl_surf_evict()`, and `qxl_vram_evict()`.

Control flow: BO creation allocates a QXL BO, initializes embedded GEM, chooses TTM placements from domain, initializes a reserved TTM BO, optionally pins it, and returns it unreserved. Mapping functions maintain `kptr` and `map_count` for vmap state, while atomic page mapping uses write-combining io mappings for VRAM/surface memory and falls back to vmap for system memory. `qxl_bo_check_id()` lazily allocates and creates a host surface for surface-domain BOs.

State and persistence: Per-BO state includes TTM resource placement, placement arrays, map state, pin count, surface metadata, `surface_id`, `hw_surf_alloc`, and optional shadow pointer. Device state includes GEM object list mutations and global memory managers evicted by helper functions.

Dependencies and integration points: Used throughout QXL display, draw, image, release, ioctl, PRIME, and KMS code. Depends on TTM, DRM GEM object funcs, io_mapping, QXL command surface creation, and the object header inline reserve helpers.

Risks: Mapping fallback calls `qxl_bo_vmap_locked()` and later unmaps in `qxl_bo_kunmap_atomic_page()`; callers must hold reservation where required. `qxl_bo_create()` returns directly after failed `ttm_bo_init_reserved()` without releasing the initialized GEM object, which should be audited. Surface creation on validation can fail after assigning an ID, requiring cleanup scrutiny.

Test signals: BO allocation in VRAM, surface, and CPU domains; pin/vmap nesting and map_count behavior; eviction of surface BOs during TTM moves; PRIME vmap paths; forced allocation/TTM validation failures; lockdep with reservation assertions.
