<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tile.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tile.c

## Purpose

`xe_tile.c` allocates and initializes per-tile Xe driver resources: GGTT, migration helpers, VRAM region structures, pagemap caches, sysfs, memory IRQs, and suballocation pools.

## Important APIs, Types, and Functions

`xe_tile_init_early()` stores the backpointer/ID, allocates GGTT and migration objects, and initializes PCODE state. `xe_tile_alloc_vram()` creates a tile VRAM region on discrete devices. `xe_tile_init_noalloc()` applies tile workarounds, creates pagemap cache, initializes TTM VRAM manager when needed, updates memory-region mask, and creates tile sysfs. `xe_tile_init()` initializes memory IRQs and kernel/reclaim suballocator pools. `xe_tile_migrate_wait()` waits on migration work. `xe_tile_local_pagemap()` returns an active local pagemap when pagemap support is enabled.

## Control Flow

Probe runs early init before hardware-dependent setup, allocates VRAM structs for DGFX, runs noalloc initialization before allocations that could disturb inherited display framebuffers, then runs full init for runtime resources.

## State and Persistence Behavior

Tile fields persist in `struct xe_tile`: `xe`, `id`, GGTT, migrate helper, VRAM/kernel VRAM, kernel BB pool, reclaim pool, memirq, pcode lock, sysfs kobject, debugfs dentry, SR-IOV tile state, and MERT state.

## Dependencies and Integration Points

The file integrates DRM managed allocation, GGTT, migration, PCODE, workarounds, tile sysfs, TTM VRAM manager, SVM pagemap caches, memory IRQs, suballocators, and VRAM region management.

## Risks and Test Signals

Risks include initialization ordering around display readout, memory-region mask updates, DGFX-only VRAM paths, and pagemap cache availability before SVM faults. Tests should cover single/multi-tile init order, allocation failure injection, DGFX versus integrated paths, noalloc behavior, and pagemap-enabled/disabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tile.c -->
