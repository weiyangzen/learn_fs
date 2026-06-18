<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_reset.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_reset.h

Purpose: declares the GT/engine reset, wedge, error handling, and reset-lock APIs used across i915.

Important APIs: `intel_gt_init_reset/fini_reset`, `intel_gt_handle_error()`, `intel_gt_reset()`, `intel_engine_reset()`, `__intel_engine_reset_bh()`, `__i915_request_reset()`, reset trylock/interruptible lock/unlock, `intel_gt_set_wedged()`, `intel_gt_unset_wedged()`, `intel_gt_terminally_wedged()`, wedge-on-init/fini markers, `intel_gt_reset_engine()`, `intel_gt_reset_all_engines()`, `intel_reset_guc()`, `intel_wedge_on_timeout()` helper macro, `intel_has_gpu_reset()`, `intel_has_reset_engine()`, and `intel_engine_reset_needs_wa_22011802037()`. `I915_ERROR_CAPTURE` controls error-state capture.

Control flow: users report hangs through `intel_gt_handle_error()` or direct engine/global reset APIs; code needing protection from reset uses the SRCU reset lock helpers; long reset sections can use `intel_wedge_on_timeout()` to schedule automatic wedging.

State and persistence: declarations operate on `struct intel_reset` embedded in the GT, request error state, and engine reset flags.

Dependencies and integration points: includes compiler/types/SRCU, engine types, and reset types. Used by request allocation/submission, hangcheck, display reset, GuC code, and GEM error paths.

Risks: reset lock users must always release the SRCU tag. `__intel_engine_reset_bh()` is bottom-half-oriented and has stricter context expectations than `intel_engine_reset()`. Wedge-on-init/fini are intentionally irreversible.

Test signals: reset API build coverage, lock/unlock pairing tests, hangcheck selftests, and wedge timeout tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_reset.h -->
