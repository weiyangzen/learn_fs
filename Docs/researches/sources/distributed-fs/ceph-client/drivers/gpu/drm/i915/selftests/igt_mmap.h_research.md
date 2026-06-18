# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/igt_mmap.h

## Purpose
This header declares mmap helpers for i915 selftests.

## Important APIs, Types, And Functions
It forward-declares `drm_i915_private`, `drm_vma_offset_node`, and `file`, and declares `igt_mmap_offset()` plus `igt_mmap_offset_with_file()`.

## Control Flow
Callers choose either the convenience path that creates a mock file or the explicit file path when they already own a DRM file.

## State And Persistence
The header has no state. Successful mappings and temporary node permissions are handled by the implementation.

## Dependencies And Integration Points
It exposes the helper without pulling in heavy DRM headers. GEM mmap selftests use it to drive mmap paths from kernel tests.

## Risks
The API returns `unsigned long`, so callers must use mmap error conventions when checking failures.

## Test Signals
Signals are returned addresses or encoded errnos from the implementation.
