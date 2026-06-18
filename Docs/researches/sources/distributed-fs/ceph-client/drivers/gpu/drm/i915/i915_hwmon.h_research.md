# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_hwmon.h

## Purpose
Declares the i915 hwmon lifecycle and reset coordination hooks, with no-op inline stubs when hwmon support is not reachable.

## Important APIs, types, and functions
Forward declares `struct drm_i915_private` and `struct intel_gt`. Exposes `i915_hwmon_register()`, `i915_hwmon_unregister()`, `i915_hwmon_power_max_disable()`, and `i915_hwmon_power_max_restore()` under `IS_REACHABLE(CONFIG_HWMON)`.

## Control flow
The header has no runtime control flow. Compile-time configuration selects real declarations or empty inline functions so callers do not need local `#ifdef CONFIG_HWMON` guards.

## State and persistence
No state is defined here. The implementation stores state in `i915->hwmon` and in hardware power registers.

## Dependencies and integration points
Included by hwmon implementation and i915 reset/device lifecycle code. It is the narrow API boundary between generic driver flows and the optional hwmon module.

## Risks
Stub behavior means callers must not rely on `old` being initialized when hwmon is disabled; current implementation only uses it when restore is paired with a successful disable path.

## Test signals
Compile with hwmon enabled, disabled, and as module-reachable to catch declaration/stub mismatches.
