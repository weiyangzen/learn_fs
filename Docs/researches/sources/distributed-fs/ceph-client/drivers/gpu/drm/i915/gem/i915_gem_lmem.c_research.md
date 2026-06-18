# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_lmem.c

## Purpose
Provides helpers for GEM objects resident in local memory (LMEM): WC iomapping, residency checks, and constructors for LMEM-backed objects.

## Important APIs and Functions
`i915_gem_object_lmem_io_map()` maps a contiguous LMEM object range through the region `io_mapping`. `i915_gem_object_is_lmem()` checks local-memory residency. `__i915_gem_object_create_lmem_with_ps()` creates LMEM with explicit page-size constraints. `i915_gem_object_create_lmem()` creates a normal LMEM object. `i915_gem_object_create_lmem_from_data()` creates a contiguous object, WC maps it, copies initial data, flushes, and releases the map.

## Control Flow
Creation delegates to `i915_gem_object_create_region()` for `INTEL_REGION_LMEM_0`. The data helper page-rounds size, requests contiguous backing, pins a WC map, copies caller data, flushes CPU writes, releases the mapping, and drops the object on failure. The IO map helper asserts contiguous backing and computes a region-relative offset from the object DMA address.

## State and Persistence Behavior
Residency is tracked in `obj->mm.region` and memory-region allocation metadata. Data construction persists caller bytes into LMEM and flushes them for device visibility. Explicit page size affects allocation granularity and final rounded object size.

## Dependencies and Integration Points
Depends on `intel_memory_region`, GEM region allocation, object DMA lookup, object map/flush APIs, and region IDs. Display scanout code uses the LMEM residency check on LMEM-capable platforms.

## Risks
IO mapping assumes contiguous objects. Forced page sizes below region minimum can create objects that cannot be inserted into a GTT. WC data writes must be flushed. Residency checks on migratable objects require locking or pinning.

## Test Signals
LMEM allocation, migration, placement, and display/framebuffer tests exercise behavior. Assertions catch non-contiguous IO map misuse.
