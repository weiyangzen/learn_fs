# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/i915_vma.c

## Purpose
This file tests VMA creation, lookup, pinning, GTT view remapping, rotated views, partial views, and live GGTT remapped IO behavior. It verifies both metadata identity and the scatterlist/page ordering generated for non-normal GTT views.

## Important APIs, Types, And Functions
- Public entries are `i915_vma_mock_selftests()` and `i915_vma_live_selftests()`.
- `checked_vma_instance()` wraps `i915_vma_instance()` and validates `i915_vma_compare()`.
- `igt_vma_create()` creates many objects and mock contexts, then checks VMA creation and lookup under pinned/unpinned states.
- `igt_vma_pin1()` exercises boundary cases for `i915_vma_pin()` flags and sizes.
- `assert_rotated()`, `assert_remapped()`, `rotated_index()`, `remapped_index()`, and `remapped_size()` validate view scatterlists.
- `igt_vma_rotate_remap()` tests rotated and remapped mock views with two planes.
- `igt_vma_partial()` validates partial GTT views and reuse.
- `igt_vma_remapped_gtt()` writes through live remapped/rotated GGTT mappings and verifies through the normal view.

## Control Flow
Mock setup creates a mock device and GGTT, then runs VMA subtests. Creation tests grow object/context counts by primes and use two passes to pin and unpin all VMA combinations. Pin tests iterate a table of expected valid, `-EINVAL`, and `-ENOSPC` cases. Remap tests enumerate many plane geometry combinations and prime offsets, pin view VMAs, inspect scatterlists, unbind, and reschedule. Partial tests build every prime-sized window within a 1021-page object, assert pages match source DMA addresses, and check object VMA list counts. Live tests use a mappable GGTT view, write coordinates through transformed views, then read expected coordinates from normal backing offsets.

## State And Persistence
State is transient GEM objects, mock contexts, VMAs, pinned mappings, and IO mappings. Mock setup initializes and tears down a GGTT. Live tests hold runtime PM while performing IO mapping. VMAs remain on object lists during an object lifetime but disappear when objects are released.

## Dependencies And Integration Points
It depends on GEM object internals, context VM lookup, GGTT pinning, VMA comparison, scatterlist iteration, transformed GTT view structures, runtime PM, and mock GTT setup. It integrates with mock and live registries under `vma`.

## Risks
The tests assert internal VMA list counts and scatterlist shapes, so changes in VMA caching or coalescing can require corresponding test updates. Live IO mapping depends on aperture availability and correct cache/domain transitions. Pin boundary cases encode assumptions about flag bits and mappable/total GGTT boundaries.

## Test Signals
Signals include correct VM/size/view type, `i915_vma_compare()` equality, expected pin errno, exact transformed DMA ordering, no use of original pages for transformed views, exact partial page mapping, unchanged VMA list counts after normal full-view lookup, and correct live readback through normal mapping.
