# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_ttm_vram_mgr_types.h

Purpose: Defines the data structures backing Xe's VRAM TTM manager and its allocated resources.

Important APIs/types/functions: `struct xe_ttm_vram_mgr` contains a `ttm_resource_manager`, DRM `gpu_buddy`, CPU-visible size/accounting, default page size, allocation mutex, and TTM memory type. `struct xe_ttm_vram_mgr_resource` contains the base TTM resource, buddy block list, visible bytes consumed, and buddy allocation flags.

Control flow: These structures are initialized by `__xe_ttm_vram_mgr_init`, mutated by allocation/free callbacks, queried by debug/accounting helpers, and embedded by the stolen-memory manager.

State and persistence behavior: Manager fields persist for device lifetime. Resource fields persist for each BO's residency in VRAM/stolen placement. The mutex protects buddy allocation and visible accounting.

Dependencies and integration points: Includes Linux GPU buddy and TTM device APIs. Used by `xe_ttm_vram_mgr.c`, `xe_ttm_vram_mgr.h`, and `xe_ttm_stolen_mgr.c`.

Risks: The comment typo "Proped" is harmless, but the semantics are important: `visible_size` is the CPU-visible aperture, not total VRAM. Incorrect lock discipline around `visible_avail` or `blocks` would corrupt allocations.

Test signals: Structural validation comes from allocation/free stress, lockdep, and teardown accounting assertions that `visible_avail` returns to `visible_size`.
