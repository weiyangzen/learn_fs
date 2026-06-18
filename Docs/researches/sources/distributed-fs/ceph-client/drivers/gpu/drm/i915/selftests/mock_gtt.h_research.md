# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/mock_gtt.h

Purpose: declares mock GTT helpers for i915 selftests.

Important APIs: `mock_init_ggtt(struct intel_gt *gt)`, `mock_fini_ggtt(struct i915_ggtt *ggtt)`, and `mock_ppgtt(struct drm_i915_private *i915, const char *name)`.

Control flow and state: no state in the header. Callers initialize the GT GGTT during mock device setup, optionally create PPGTTs for tests, and finalize the GGTT during release.

Dependencies and integration: forward declares i915 private, GGTT, and GT structures. Implementation integrates with address-space and VM operations.

Risks: the `name` argument is currently unused by the implementation, so tests should not rely on named diagnostics from this helper.

Test signals: successful mock device creation and VM tests that can bind/unbind without touching hardware.
