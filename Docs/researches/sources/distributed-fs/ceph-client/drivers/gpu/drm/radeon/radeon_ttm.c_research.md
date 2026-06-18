<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_ttm.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_ttm.c

## Purpose
`radeon_ttm.c` connects the Radeon BO layer to the DRM TTM memory manager. It initializes VRAM/GTT managers, chooses eviction placements, moves BOs by GPU blit or CPU memcpy, maps BO resources to bus addresses, manages GTT backing pages including userptr pages, and exposes memory debugfs views.

## Important APIs, types, and functions
The TTM driver callbacks are collected in `radeon_bo_driver`: `radeon_ttm_tt_create`, populate/unpopulate, destroy, eviction policy, move, and IO memory reservation. Public APIs include `radeon_ttm_init`, `radeon_ttm_fini`, `radeon_ttm_set_active_vram_size`, `radeon_ttm_tt_set_userptr`, `radeon_ttm_tt_is_bound`, `radeon_ttm_tt_has_userptr`, and `radeon_ttm_tt_is_readonly`. Internal helpers cover `radeon_evict_flags`, `radeon_move_blit`, `radeon_bo_move`, GART bind/unbind, userptr pin/unpin, and debugfs file operations.

## Control flow
Initialization creates the TTM device with the Radeon callback table, initializes VRAM and GTT range managers, constrains active VRAM to visible VRAM, reserves/pins a stolen VGA memory BO, and registers debugfs files. Moves bind TT memory when entering GTT, wait on the BO, handle null/system transitions cheaply, request multihop moves through TT for system-to-VRAM cases, try accelerated copy when the copy ring is ready, and fall back to memcpy. GTT backend bind pins userptr pages when present, builds DMA addresses, sets GART flags, and calls `radeon_gart_bind`; unbind reverses userptr pinning and GART mappings.

## State, dependencies, and integration points
Persistent state includes `rdev->mman.bdev`, TTM resource managers, the TTM page pool, stolen VGA memory BO, GART mappings, userptr metadata in `struct radeon_ttm_tt`, and movement statistics. It depends on Linux DMA, get_user_pages, sg tables, TTM, DRM PRIME, AGP helpers, Radeon BO/GART/copy/fence code, and debugfs. It is central to GEM, command validation, VM mappings, copy acceleration, and suspend/fini ordering.

## Risks and test signals
High-risk areas are userptr lifetime/security, dirtying writable user pages, DMA mapping direction, AGP vs PCIe backend divergence, visible-VRAM bus mapping, multihop move correctness, and fallback after accelerated copy failures. Test signals include BO allocation/move stress, userptr tests, PRIME/import paths, GART bind/unbind validation, debugfs VRAM/GTT reads, suspend/resume, and fence-protected eviction behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_ttm.c -->
