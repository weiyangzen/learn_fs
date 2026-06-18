<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_rc6_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_rc6_types.h

Purpose: defines the RC6 residency enum and persistent RC6 software state for each GT.

Important types: `enum intel_rc6_res_type` identifies locked RC6, RC6, RC6p, RC6pp, and VLV media alias counters. `struct intel_rc6` stores residency register IDs, previous hardware counters, accumulated software-extended residency, enable control value, captured BIOS state, optional power-context GEM object, and boolean flags for supported/enabled/manual/wakeref/bios capture.

Control flow: `intel_rc6.c` initializes register IDs and flags, updates counters during residency reads, and uses flags to gate enable/disable/park behavior.

State and persistence: all fields persist for the GT lifetime. `prev_hw_residency` and `cur_residency` implement wrap-tolerant counter extension. `pctx` owns VLV/CHV stolen power-context backing while RC6 support is active.

Dependencies and integration points: includes spinlock/types and `intel_engine_types.h` for `i915_reg_t`; forward-declares GEM object. Embedded in GT type definitions.

Risks: counter arrays must stay indexed consistently with `enum intel_rc6_res_type`. Bitfields must be updated under lifecycle ordering that protects runtime PM and hardware access.

Test signals: residency wrap tests, init/fini leak checks for `pctx`, and platform register ID validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_rc6_types.h -->
