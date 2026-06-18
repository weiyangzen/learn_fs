# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/mock_gem_device.h

Purpose: declares the mock GEM device lifecycle functions used by i915 selftests.

Important APIs: `mock_gem_device()` returns a fully initialized mock `drm_i915_private *` or `NULL`; `mock_device_flush()` drains mock engine work and retires requests; `mock_destroy_device()` releases the mock device.

Control flow and state: the header does not own state but defines the expected lifecycle: create, run tests, flush if needed, destroy.

Dependencies and integration: forward declares `struct drm_i915_private`; implementation ties into DRM/i915 mock infrastructure.

Risks: tests must not use the pointer after `mock_destroy_device()`. Any new mock subsystem initialized in the `.c` file should be included in release cleanup.

Test signals: compile use by GEM and GT selftests plus leak-free create/destroy loops.
