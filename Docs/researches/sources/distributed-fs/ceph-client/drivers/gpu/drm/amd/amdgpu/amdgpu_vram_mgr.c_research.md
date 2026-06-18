# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_vram_mgr.c

## Purpose

This file implements AMDGPU's VRAM TTM resource manager on top of `gpu_buddy`. It allocates and frees VRAM blocks, tracks visible VRAM usage, handles reserved ranges, exports VRAM resources as scatter-gather tables, reports sysfs memory information, supports placement compatibility/intersection checks, and records task ownership for block-address queries.

## Important APIs, types, and functions

The TTM manager callbacks are in `amdgpu_vram_mgr_func`: `amdgpu_vram_mgr_new()`, `amdgpu_vram_mgr_del()`, `amdgpu_vram_mgr_intersects()`, `amdgpu_vram_mgr_compatible()`, and `amdgpu_vram_mgr_debug()`. Exported/helper APIs include `amdgpu_vram_mgr_bo_visible_size()`, `amdgpu_vram_mgr_reserve_range()`, `amdgpu_vram_mgr_query_page_status()`, `amdgpu_vram_mgr_query_address_block_info()`, `amdgpu_vram_mgr_alloc_sgt()`, `amdgpu_vram_mgr_free_sgt()`, `amdgpu_vram_mgr_vis_usage()`, `amdgpu_vram_mgr_clear_reset_blocks()`, `amdgpu_vram_mgr_init()`, and `amdgpu_vram_mgr_fini()`. Sysfs attributes expose total/visible/used/vendor memory information.

## Control flow, state, and persistence behavior

Init registers a DRM memory cgroup region, initializes the TTM resource manager with real VRAM size, initializes locks and reservation/allocation lists, initializes `gpu_buddy`, installs the VRAM manager for `TTM_PL_VRAM`, and marks it used. Allocation computes placement bounds, reserves top VRAM for VM page tables for non-kernel BOs, chooses contiguous or THP-sized chunks, applies buddy flags for top-down/range/clear/DCC, allocates blocks under `mgr->lock`, records current task pid/comm, optionally trims DCC-aligned contiguous allocations, calculates `res->start`, visible usage, contiguity, and bus caching, then returns the TTM resource. Free removes task ownership, frees blocks back to buddy, replays pending reservations, updates visible usage, finalizes the resource, and frees it.

Reserved ranges are stored first in `reservations_pending`; `amdgpu_vram_mgr_do_reserve()` attempts to allocate them from buddy, moves successful reservations to `reserved_pages`, and accounts usage. Visible usage is tracked in `mgr->vis_usage` and computed per buddy block against `adev->gmc.visible_vram_size`. SG export walks resource blocks, maps physical VRAM aperture ranges with `dma_map_resource()`, and builds an `sg_table`.

## Dependencies and integration points

The file depends on TTM resource management, DRM cgroups, `gpu_buddy`/DRM buddy helpers, DMA mapping, AMDGPU BO flags, GMC sizing, resource cursors, sysfs, and debug printers. It integrates with BO placement/eviction, dma-buf/peer export through SG tables, memory accounting, VRAM vendor reporting, and reset clear-state management.

## Risks and test signals

Risks include buddy allocation fragmentation, incorrect visible usage accounting, DCC alignment trimming mistakes, over-reserving VRAM, non-contiguous fallback behavior for supposedly contiguous BOs, SG map/unmap leaks, and stale `allocated_vres_list` task ownership. Test signals include VRAM allocation stress with mixed sizes, contiguous allocation fallback, visible VRAM sysfs values matching allocations, reserved firmware ranges surviving allocations, dma-buf export/import of VRAM, debugfs buddy dumps, and clean manager fini after evict-all.
