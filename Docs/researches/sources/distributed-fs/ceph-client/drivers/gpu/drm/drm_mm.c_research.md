# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_mm.c

## Purpose
This file implements `drm_mm`, DRM's generic range allocator for GPU address spaces and similar driver-managed regions. It tracks allocated `drm_mm_node` ranges, free holes, interval overlap queries, range-restricted allocation, optional color-based placement adjustments, LRU-style eviction scanning, leak debugging, and allocator state dumping.

## Important APIs, Types, and Functions
The public lifecycle API is `drm_mm_init()`, `drm_mm_takedown()`, and `drm_mm_print()`. Allocation APIs are `drm_mm_reserve_node()` for caller-preselected ranges, `drm_mm_insert_node_in_range()` for searched allocations, and `drm_mm_remove_node()` for O(1) removal. Eviction scan APIs are `drm_mm_scan_init_with_range()`, `drm_mm_scan_add_block()`, `drm_mm_scan_remove_block()`, and `drm_mm_scan_color_evict()`. Overlap lookup is exposed through `__drm_mm_interval_first()`.

Internally, allocated nodes live in a linked list ordered by address and an interval tree keyed by `[start, last]`. Holes are represented as the gap following an allocated node or the synthetic `head_node`; the same hole is indexed in `hole_stack`, `holes_size`, and `holes_addr`. Helper paths include `add_hole()`, `rm_hole()`, `best_hole()`, `find_hole_addr()`, `first_hole()`, and `next_hole()`.

## Control Flow
Initialization creates a synthetic `head_node` with `start + size` and negative `size`, then adds one hole covering the managed range. Insert-by-search first rejects impossible sizes/ranges, checks the largest hole, normalizes alignment, selects an initial hole according to bottom-up, top-down, best, or eviction mode, applies optional `color_adjust`, intersects with the caller range, aligns the candidate start, and inserts the node into the list and interval tree. The source hole is removed and replaced with left and/or right residual holes.

Reservation follows a similar split path but starts from a caller-provided `node->start`, `node->size`, and `node->color`. Removal deletes any following hole, removes the node from the interval tree and node list, merges with the previous node's following hole, and clears the allocated bit. Scanning temporarily removes candidate nodes from the address list without poisoning their list pointers, computes whether the resulting enlarged hole can satisfy the requested allocation, and requires callers to restore candidates in exact reverse order.

## State and Persistence Behavior
All allocator state is in the caller-owned `struct drm_mm` and caller-owned `struct drm_mm_node`s; the allocator performs no allocation for normal operations. Persistent fields include list membership, RB nodes, interval tree augmentation, hole sizes, color tags, flags, and scan state. With `CONFIG_DRM_DEBUG_MM`, stack depot handles are saved on insertion to report leaked nodes at takedown. The implementation is explicitly not thread-safe; drivers must provide external locking around all mutations.

## Dependencies and Integration Points
The file depends on Linux interval tree/RB tree helpers, lists, stack traces, stack depot under debug config, and DRM printer/debug macros. GPU drivers use it for GTT/VRAM/aperture and other address-space allocation when Linux's resource allocator is not a good match. The `color_adjust` callback is the main integration hook for driver-specific placement constraints such as guard pages between incompatible cache domains.

## Risks
Incorrect external locking can corrupt multiple trees/lists at once. Range arithmetic is `u64`; callers must avoid overflow and zero-sized nodes. Alignment code handles power-of-two and arbitrary alignment differently, so edge cases need coverage. The scan API is fragile by design: removing scan blocks out of reverse order corrupts the allocator, and no unrelated operations are allowed while `scan_active` is nonzero. Color adjustment can shrink holes enough to require extra eviction via `drm_mm_scan_color_evict()`. Takedown only warns on leaks; callers remain responsible for removing all nodes.

## Test Signals
Signals include allocator selftests or KUnit-style insert/remove/reserve coverage, bottom-up/top-down/best/evict placement, alignment with power-of-two and non-power-of-two values, range restriction rejection, interval overlap lookup correctness, color adjustment guard behavior, scan add/remove reverse-order behavior, leak reporting under `CONFIG_DRM_DEBUG_MM`, and `drm_mm_print()` totals matching allocated plus free space.
