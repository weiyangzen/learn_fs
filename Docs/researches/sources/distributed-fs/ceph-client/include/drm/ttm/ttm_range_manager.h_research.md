# sources/distributed-fs/ceph-client/include/drm/ttm/ttm_range_manager.h

Purpose: declares a DRM-MM-backed TTM resource manager for range-based address spaces such as VRAM apertures.

Important APIs/types/functions: `struct ttm_range_mgr_node` extends `ttm_resource` with a flexible array of `drm_mm_node`s. `to_ttm_range_mgr_node()` downcasts from base resource. `ttm_range_man_init_nocheck()` and `ttm_range_man_fini_nocheck()` install/remove the manager; inline checked wrappers validate constant memory type bounds.

Control flow: driver init registers a range manager for a memory type and size. Resource allocation uses DRM MM nodes behind the manager; fini removes it when empty.

State and persistence: range manager state lives in the TTM device manager slot and DRM MM nodes embedded in resources.

Dependencies and integration: depends on TTM resource/device and DRM MM. Used by TTM drivers for VRAM or other linear address spaces.

Risks and test signals: finishing with live allocations, wrong memory type index, and multi-node resource handling are risks. Test manager init/fini, allocation/free fragmentation, bound checks, and eviction of all resources before fini.
