# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/selftests/i915_gem_object.c

## Purpose
Provides basic GEM object selftests: mock shmem object creation and live sanity checking for the huge fake object helper.

## APIs And Control Flow
Defines `igt_gem_object()`, `igt_gem_huge()`, `i915_gem_object_mock_selftests()`, and `i915_gem_object_live_selftests()`. The mock test creates and releases a one-page shmem object. The live test creates a huge fake object larger than its real backing, pins pages, and verifies page lookup wraps to the expected real page by modulo index.

## State, Dependencies, Integration, Risks, And Tests
State is transient in mock/live devices and GEM page arrays. Dependencies include `huge_gem_object`, mock GEM setup, and GT GGTT sizing. Risks are changed fake-object wrapping semantics or pin-page behavior. Signals are creation/pin failures and page lookup mismatches.
