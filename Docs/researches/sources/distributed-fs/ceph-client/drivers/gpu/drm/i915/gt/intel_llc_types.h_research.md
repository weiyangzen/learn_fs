<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_llc_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_llc_types.h

Purpose: defines the `struct intel_llc` storage type used as an embedded marker inside `struct intel_gt`.

Important type: `struct intel_llc` is currently empty; it exists to provide a typed subobject for LLC enable/disable APIs and future state.

Control flow: implementation functions use `container_of(llc, struct intel_gt, llc)` to reach the GT.

State and persistence: no fields are stored today. Hardware-side LLC/ring-frequency state is programmed by `intel_llc.c`.

Dependencies and integration points: no includes beyond guards; included by GT type declarations and `intel_llc.h`.

Risks: because the struct is empty, its only semantic value is its embedding location. Moving or duplicating it without updating `llc_to_gt()` assumptions would break runtime behavior.

Test signals: build coverage and LLC enable selftests on platforms with shared LLC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_llc_types.h -->
