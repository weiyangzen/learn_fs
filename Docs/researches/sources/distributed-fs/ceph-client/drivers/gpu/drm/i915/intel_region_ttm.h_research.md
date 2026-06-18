# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_region_ttm.h

Purpose: declares the TTM integration surface for i915 memory regions.

Important APIs/functions: exposes TTM device init/fini, region init/fini, TTM type mapping, resource-to-refcounted-SG conversion, resource free, `i915_ttm_driver()`, and selftest-only resource allocation.

Control flow: memory-region setup calls `intel_region_ttm_init()` for suitable regions after the global TTM device exists; teardown calls fini/free functions in reverse. GEM backends call conversion helpers after TTM allocation.

State and persistence: no state in the header; state resides in the TTM device and each region's `region_private`.

Dependencies and integration: includes i915 selftest declarations, forward-declares TTM and i915 types, and provides the boundary between memory-region code and TTM allocation internals.

Risks: selftest-only declarations are hidden behind `CONFIG_DRM_I915_SELFTEST`; production code must not depend on them. Callers must pass resources from the matching region manager to avoid freeing through the wrong manager.

Test signals: build coverage with and without selftests, local-memory allocation tests, and TTM teardown checks.
