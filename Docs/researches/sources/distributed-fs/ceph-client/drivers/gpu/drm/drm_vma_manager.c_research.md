# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_vma_manager.c

## Purpose
Provides DRM's page-based mmap offset manager for mapping driver memory objects into a single DRM device address space, plus per-open-file access control for mmap permission checks.

## Important APIs, Types, and Functions
Exports manager lifecycle (`drm_vma_offset_manager_init/destroy`), offset allocation (`drm_vma_offset_add/remove`), lookup (`drm_vma_offset_lookup_locked`), and access control (`drm_vma_node_allow`, `drm_vma_node_allow_once`, `drm_vma_node_revoke`, `drm_vma_node_is_allowed`). It uses `struct drm_mm` for allocation and rb-trees for both interval lookup and allowed-file tracking.

## Control Flow
Managers initialize a page-range-backed `drm_mm`. Adding a node inserts into `drm_mm` under write lock unless already allocated; removing deletes and zeroes the `drm_mm_node`. Lookup walks the interval tree for the best node with `start <= requested_start`, then verifies it spans the requested page range. Access allow preallocates a permission entry, inserts or increments by `struct drm_file *` tag under node lock, and revoke decrements/removes entries.

## State and Persistence
Offset allocations persist in memory until explicit removal. Allowed-file rb-tree entries persist across offset add/remove and must be balanced by revocation before node destruction. No disk persistence exists.

## Dependencies and Integration Points
Depends on `drm_mm`, Linux rb-tree APIs, DRM GEM mmap offset helpers, and callers holding lookup locks for weak-reference lookup patterns.

## Risks
Using multiple managers on one address_space breaks linear mmap teardown assumptions. Permission entries can leak if allow/revoke counts are unbalanced. Callers must keep nodes alive during locked lookup and remove all nodes before manager destruction.

## Test Signals
Test non-overlap allocation, lookup inside object ranges, mmap access denied/allowed/revoked, repeated allow/revoke reference counts, destruction with empty manager, and concurrent lookup/remove lock discipline.
