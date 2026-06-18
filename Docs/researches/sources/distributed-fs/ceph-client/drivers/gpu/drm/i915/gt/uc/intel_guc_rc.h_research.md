## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_rc.h

Purpose: declares GuC RC support/selection helpers and enable/disable entry points.

Important APIs, types, and functions:
- `intel_guc_rc_init_early()` initializes support and selection booleans.
- Inline helpers `intel_guc_rc_is_supported()`, `intel_guc_rc_is_wanted()`, and `intel_guc_rc_is_used()` compose support, GuC submission selection, and actual GuC submission use.
- `intel_guc_rc_enable()` and `intel_guc_rc_disable()` control firmware/host RC mode.

Control flow:
- Higher-level UC init code checks these helpers to decide whether to invoke GuC RC enable/disable.

State and persistence:
- Reads `guc->rc_supported`, `guc->rc_selected`, and submission state; no header-owned state.

Dependencies and integration points:
- Includes `intel_guc_submission.h` to access `struct intel_guc` and submission predicates.

Risks:
- `intel_guc_rc_is_wanted()` depends on `submission_selected`; if selection changes after early init, callers need current state consistency.

Test signals:
- Compile coverage and policy matrix tests for supported/wanted/used combinations.
