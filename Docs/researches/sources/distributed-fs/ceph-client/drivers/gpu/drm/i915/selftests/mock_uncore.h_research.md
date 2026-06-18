# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/mock_uncore.h

Purpose: declares mock uncore initialization.

Important API: `mock_uncore_init(struct intel_uncore *uncore, struct drm_i915_private *i915)`.

Control flow and state: no header state; caller supplies the uncore storage and owning i915 device.

Dependencies and integration: forward declares i915 private and uncore structures. Implementation integrates with early uncore setup and raw MMIO vfunc assignment.

Risks: the initialized uncore is intentionally non-persistent for MMIO values, so consumers must be mock-aware.

Test signals: mock GEM device creation can initialize uncore without hardware register mappings.
