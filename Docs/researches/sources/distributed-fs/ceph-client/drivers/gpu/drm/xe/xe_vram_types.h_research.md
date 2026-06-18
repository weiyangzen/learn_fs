# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_vram_types.h

## Purpose

`xe_vram_types.h` defines `struct xe_vram_region`, the driver representation of a local-memory region such as HBM, tile-local VRAM, or future extension memory.

## Important APIs, Types, and Functions

`struct xe_vram_region` stores a back pointer to `xe_device`, unique region id, CPU-visible IO start and size, device physical address base, usable size excluding reserved memory, actual physical size including reserved memory, BAR mapping pointer, embedded `xe_ttm_vram_mgr`, TTM placement id, and optional pagemap/migration fields under `CONFIG_DRM_XE_PAGEMAP`.

## Control Flow and State

The structure is allocated and initialized by `xe_vram.c` during dGFX probe. Its fields persist for the device lifetime and are cleared in managed cleanup for mapping pointers. The TTM manager and optional pagemap cache use the region to represent allocatable device memory.

## Dependencies and Integration Points

The type depends on `xe_ttm_vram_mgr_types.h` and conditionally on `drm_pagemap.h`. It is shared with VRAM probing, TTM placement setup, memory migration, pagemap integration, and any caller that needs concrete region fields.

## Risks and Edge Cases

Callers must distinguish `io_size` from `usable_size`: small BAR devices can have less CPU-visible VRAM than device-usable VRAM. `actual_physical_size` includes stolen/reserved regions, while `usable_size` does not. Conditional pagemap fields require configuration-aware initialization and teardown.

## Test Signals

Probe tests should verify all fields are populated consistently for single-tile, multi-tile, small BAR, and pagemap-enabled builds. Static/build coverage should catch configuration-dependent field users.
