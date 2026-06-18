## sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_ttm.c

### Purpose

`lsdc_ttm.c` implements Loongson LSDC buffer-object storage on top of DRM TTM. It owns placement selection for VRAM, TT/GTT, and system memory, BO movement and eviction policy, kernel mapping helpers, pinned kernel BO allocation, TTM resource-manager initialization, and debugfs exposure for the VRAM/GTT managers.

### Important APIs, types, and functions

The file exports `lsdc_mem_type_to_str()`, `lsdc_domain_to_str()`, `lsdc_bo_create()`, `lsdc_bo_create_kernel_pinned()`, `lsdc_bo_free_kernel_pinned()`, reserve/unreserve, pin/unpin, ref/unref, `lsdc_bo_gpu_offset()`, `lsdc_bo_size()`, kmap/kunmap/clear, `lsdc_bo_evict_vram()`, `lsdc_ttm_init()`, and `lsdc_ttm_debugfs_init()`. The TTM callback table `lsdc_bo_driver` provides TT creation/populate/unpopulate/destroy, eviction placement, movement, and IO bus reservation.

### Control flow

BO creation allocates `struct lsdc_bo`, initializes the embedded GEM object and TTM BO, selects a BO type from kernel/sg/device inputs, fills `ttm_placement`, then calls `ttm_bo_init_validate()`. Placement prefers requested LSDC domains and falls back to system memory; page-sized objects get TOPDOWN placement. Pinning optionally revalidates to a requested domain, updates `vram_pinned_size` or `gtt_pinned_size`, increments TTM pin count, and returns a GPU offset for non-system placements. Movement waits for fences, handles null/system/TT transitions cheaply, and uses memcpy for real memory moves. Initialization creates the TTM device plus VRAM and TT range managers and registers managed teardown.

### State and persistence behavior

Persistent driver state is in `struct lsdc_bo` placement arrays, maps, pin counts, list linkage, and in `struct lsdc_device` TTM device/resource managers and pinned-size counters. Hardware-visible state is the VRAM bus offset computed from `ldev->vram_base` and resource start pages. Imported scatter-gather BOs use external TT pages and only convert SG entries into DMA address arrays; they are not freed through the TTM pool.

### Dependencies

It depends on DRM GEM lifetime helpers, PRIME SG helpers, drm-managed cleanup, TTM BO/TT/range-manager APIs, DMA reservations/fences, and Loongson device helpers from `lsdc_drv.h`. Debugfs integration depends on the DRM primary minor and TTM resource-manager debugfs helpers.

### Integration points

This is the memory-management backend used by LSDC GEM, framebuffer, scanout, and kernel BO paths. Scanout users reserve and pin BOs, then consume `lsdc_bo_gpu_offset()`. Device teardown reaches `lsdc_ttm_fini()` through `drmm_add_action_or_reset()`. Debugfs exposes `vram_mm` and `gtt_mm` beneath the DRM minor root.

### Risks

Pinned objects cannot be moved; callers must reserve BOs correctly around pin/unpin. `lsdc_bo_gpu_offset()` returns zero for unpinned or system BOs, which can silently become an invalid scanout address if ignored. Imported/shared BOs are rejected for VRAM pinning, so PRIME sharing paths must tolerate placement limits. Error paths after range-manager initialization do not explicitly unwind earlier managers until managed cleanup is registered, so init ordering matters.

### Test signals

Useful signals include DRM/KMS boot with VRAM scanout, GEM BO creation/import/export, CPU mapping and clear operations on VRAM and TT, pin/unpin accounting under repeated modesets, VRAM eviction under pressure, suspend/remove cleanup, and debugfs `vram_mm`/`gtt_mm` presence.
