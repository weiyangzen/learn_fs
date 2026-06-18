# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_gem_gtt.c

## Purpose
`i915_gem_gtt.c` provides common GEM-to-GTT helpers: DMA mapping/unmapping object page tables and allocating/reserving `drm_mm_node` ranges in i915 address spaces with eviction fallback.

## Important APIs, Types, and Functions
Public functions are `i915_gem_gtt_prepare_pages()`, `i915_gem_gtt_finish_pages()`, `i915_gem_gtt_reserve()`, and `i915_gem_gtt_insert()`. The local helper `random_offset()` selects an aligned random replacement address for first-attempt eviction.

## Control Flow
`prepare_pages()` attempts bidirectional DMA mapping with skip-sync/no-kernel-mapping/no-warn attributes. If mapping fails, it repeatedly invokes the GEM shrinker for bound and unbound objects sized to the target object and retries until shrinker progress stops, then returns ENOSPC. `finish_pages()` optionally sleeps briefly for `ggtt->do_idle_maps` and unmaps the sg table.

`gtt_reserve()` validates alignment/range/node state, initializes the node, tries exact `drm_mm_reserve_node()`, and if the only failure is ENOSPC and eviction is allowed, calls `i915_gem_evict_for_node()` before retrying. `gtt_insert()` validates arguments, chooses low/high/best insertion mode from flags, normalizes small alignment to zero for `drm_mm`, tries direct insertion, optionally retries without one-shot mode, rejects no-evict, tries one random fixed reservation to avoid pathological LRU scans, and finally calls `i915_gem_evict_something()` plus an evict-mode `drm_mm_insert_node_in_range()`.

## State and Persistence Behavior
DMA mapping state persists in the sg table until `finish_pages()`. Insert/reserve mutate `node->size/start/color` and the VM's `drm_mm` allocation state. They may indirectly unbind other VMAs through eviction, changing VM bound lists and VMA binding state.

## Dependencies and Integration Points
This file depends on DMA mapping, GEM shrinker, GGTT idle-map policy, `drm_mm`, random number generation, VM cache coloring, GTT page-size constants, eviction APIs, tracepoints, and vGPU/device page-size behavior through callers. VMA bind/pin and object page preparation paths use these helpers.

## Risks
DMA remap failure recovery can trigger reclaim/eviction while the target object pages are being prepared; the code asserts it is not shrinking the same page set. Insert alignment and range checks are strict and use `GEM_BUG_ON()` for programmer errors. Random replacement avoids worst-case scans but can evict surprising objects. Flags such as `PIN_NOEVICT`, `PIN_NOSEARCH`, `PIN_MAPPABLE`, and `PIN_HIGH` materially change placement and fallback behavior.

## Test Signals
GTT selftests for direct insert, fixed reserve, random eviction, no-evict/no-search flags, low/high/mappable placement, cache-color guard pages, DMA map failure with shrinker progress, and unmap after idle-map delays.
