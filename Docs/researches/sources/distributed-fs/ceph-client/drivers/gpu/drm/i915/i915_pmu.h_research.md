# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_pmu.h

## Purpose

`i915_pmu.h` defines the i915 perf-event PMU state and public hooks used by driver lifecycle and GT power-management code. It describes which non-engine events need enable/disable tracking and how the sampling timer stores global samples.

## Important APIs, types, and functions

The header defines `enum i915_pmu_tracked_events`, sampler indices such as `__I915_SAMPLE_FREQ_ACT`, `__I915_SAMPLE_FREQ_REQ`, and `__I915_SAMPLE_RC6`, `I915_PMU_MAX_GT`, `I915_PMU_MASK_BITS`, `I915_ENGINE_SAMPLE_COUNT`, `struct i915_pmu_sample`, and `struct i915_pmu`. When `CONFIG_PERF_EVENTS` is enabled it declares `i915_pmu_register()`, `i915_pmu_unregister()`, `i915_pmu_gt_parked()`, and `i915_pmu_gt_unparked()`; otherwise it provides empty inline stubs.

## Control flow

The header itself has only conditional compilation flow. In perf-enabled builds, driver registration calls into `i915_pmu.c`; in non-perf builds, callers compile away the hooks. The event bit layout described here drives `config_bit()`, refcount arrays, timer enable decisions, and per-GT sample indexing in the implementation.

## State and persistence behavior

`struct i915_pmu` stores the registered PMU object, name, spinlock, unparked mask, hrtimer, global enable bitmask, timer timestamp, per-event refcounts, timer-enabled flag, per-GT sample arrays, RC6 sleep timestamps, interrupt counter, and sysfs attribute storage. These fields persist for the device lifetime between PMU registration and unregister.

## Dependencies

It depends on Linux hrtimer, perf_event, spinlock types, and i915 uAPI PMU constants. It forward declares `drm_i915_private` and `intel_gt` so lifecycle users do not need the full implementation.

## Integration points

`struct drm_i915_private` embeds `struct i915_pmu`. Driver registration calls `i915_pmu_register()` after core device setup and `i915_pmu_unregister()` during teardown. GT runtime PM calls parked/unparked hooks to synchronize RC6 approximation and sampling timers.

## Risks

Bit layout changes are ABI-sensitive because event configs map to enable bits and refcount indexes. `I915_PMU_MAX_GT` must match the implementation's supported GT indexing. Stubs must remain side-effect free for non-perf builds. Because `irq_count` is intentionally an unsigned long rather than atomic, writers/readers rely on tolerant wraparound semantics.

## Test signals

Build with and without `CONFIG_PERF_EVENTS`. Run perf event discovery and sampling tests on single-GT and multi-GT platforms. Exercise GT park/unpark paths and verify no unresolved symbols or dead code assumptions in non-perf builds.
