# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/vlv_suspend.h

Purpose: declares VLV suspend/resume lifecycle hooks.

Important APIs: `vlv_suspend_init()`, `vlv_suspend_cleanup()`, `vlv_suspend_complete()`, and `vlv_resume_prepare(struct drm_i915_private *i915, bool rpm_resume)`.

Control flow and state: driver setup allocates suspend snapshot state, suspend calls complete after other GT quiesce work, resume calls prepare before normal operation, and cleanup frees state.

Dependencies and integration: forward declares `drm_i915_private` and uses `linux/types.h`. Implementation integrates with VLV/CHV power management and clock gating.

Risks: hooks are no-ops on non-VLV/CHV platforms in implementation, but callers should still preserve correct ordering around GT access disable/enable.

Test signals: VLV/CHV runtime/system suspend testing and compile coverage for platform PM paths.
