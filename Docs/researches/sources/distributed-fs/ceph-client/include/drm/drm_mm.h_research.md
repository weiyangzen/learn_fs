# sources/distributed-fs/ceph-client/include/drm/drm_mm.h

Purpose: declares the DRM generic range allocator, historically used for GPU address spaces and memory heaps. It manages allocated nodes, free holes, address/size-ordered search trees, and eviction scanning.

Important APIs and types: `enum drm_mm_insert_mode` selects best-fit, low-address, high-address, eviction-hole, lowest-only, or highest-only allocation behavior. `struct drm_mm_node` represents an allocated block with start, size, color tag, list/rb-tree nodes, hole metadata, allocation/scanned flags, and optional debug stack. `struct drm_mm` owns the allocator, optional `color_adjust` callback, hole stack, sentinel head node, interval tree, hole-size/address trees, and scan state flag. `struct drm_mm_scan` stores parameters and hit range for eviction scanning. APIs reserve existing nodes, insert nodes in a range, remove nodes, initialize/take down allocators, iterate nodes/holes/ranges, initialize eviction scans, add/remove scan blocks, choose color eviction candidates, and print allocator state.

Control flow: drivers initialize an allocator with a base and size, then insert preallocated cleared nodes through `drm_mm_insert_node*()` or reserve known ranges with `drm_mm_reserve_node()`. The allocator searches holes according to mode and range constraints, applies `color_adjust` if present, inserts into all tracking structures, and updates hole metadata. Eviction flow initializes a scan, temporarily marks/removes candidate blocks to form a hole, checks if the requested allocation fits, and then removes or restores candidates.

State and persistence behavior: allocator state is entirely in memory and embedded by drivers. Nodes are driver-allocated and must be zeroed before insertion. Holes are represented implicitly as metadata on the node before the free range, including the sentinel head node. Debug builds can record allocation stack traces and use `BUG_ON` assertions.

Dependencies and integration points: uses Linux rb-trees, lists, stackdepot under `CONFIG_DRM_DEBUG_MM`, and DRM printer support. It is a lower-level allocator used by DRM memory managers and address-space code.

Risks: callers must provide external locking. Range iterator misuse outside allocator bounds can walk the sentinel and potentially loop. Node reuse without clearing violates allocation flag assumptions. Color-adjust callbacks can shrink holes incorrectly and cause false `-ENOSPC`. Eviction scanning restricts other allocator operations while active.

Test signals: allocation modes and alignment, range-limited insertion, reserved node insertion, color-adjust guard pages, hole iteration, node-in-range iteration, removal/clean checks, eviction scan add/remove decisions, debug stack output, and concurrent caller lock coverage in drivers.
