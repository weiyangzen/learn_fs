<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_reset_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_reset_types.h

Purpose: defines the persistent reset coordination state and reset flag bit layout for each GT.

Important type and constants: `struct intel_reset` contains `flags`, `mutex`, `queue`, and `backoff_srcu`. Flag bits include `I915_RESET_BACKOFF`, engine-specific bits starting at `I915_RESET_ENGINE`, and high bits `I915_WEDGED_ON_INIT`, `I915_WEDGED_ON_FINI`, and `I915_WEDGED`.

Control flow: global reset sets `I915_RESET_BACKOFF` to block reset-sensitive users and reset-engine attempts; per-engine reset uses `I915_RESET_ENGINE + engine->id`; wedging sets `I915_WEDGED`; init/fini failures add terminal wedge bits. The waitqueue wakes clients when reset backoff ends, and SRCU protects code sections that cannot race with global reset resource clobbering.

State and persistence: all fields persist for the GT lifetime. The mutex serializes wedging/unwedging. The waitqueue and SRCU manage concurrent users around reset.

Dependencies and integration points: includes mutex, waitqueue, and SRCU headers. Embedded in `struct intel_gt` and consumed by `intel_reset.c` plus callers using reset locks.

Risks: flag bit allocation must leave enough room for all engine reset bits before high wedge bits. Incorrect memory ordering around flag updates can allow execbuf or reset users through at unsafe times.

Test signals: reset flag contention tests, SRCU lock coverage, wedge/unwedge races, and build-time assertions in reset code for engine-bit layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_reset_types.h -->
