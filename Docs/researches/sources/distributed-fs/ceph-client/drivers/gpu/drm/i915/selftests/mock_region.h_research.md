# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/mock_region.h

Purpose: declares mock memory-region creation for i915 selftests.

Important API: `mock_region_create(struct drm_i915_private *i915, resource_size_t start, resource_size_t size, resource_size_t min_page_size, resource_size_t io_start, resource_size_t io_size)` returns an `intel_memory_region *` or error pointer.

Control flow and state: the caller owns the returned memory region and must release it through the standard memory-region lifecycle.

Dependencies and integration: forward declares i915 private and memory-region structures and uses `linux/types.h` for `resource_size_t`.

Risks: callers need an initialized mock-region IDA in `i915->selftest.mock_region_instances`; mock GEM device setup performs this initialization.

Test signals: region tests should create mock regions of different sizes/page sizes and exercise GEM object allocation.
