# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_ggtt_gmch.h

## Purpose
This header exposes the legacy GMCH GGTT hooks when building on x86 and provides safe `-ENODEV`/no-op stubs on non-x86 platforms.

## Important APIs, Types, and Functions
The x86 declarations are `intel_ggtt_gmch_flush()`, `intel_ggtt_gmch_enable_hw()`, and `intel_ggtt_gmch_probe()`. Non-x86 inline stubs keep callers buildable while preventing use of the x86-only backend.

## Control Flow
There is no internal flow. `intel_ggtt.c` calls these functions when the platform generation requires old GMCH support or when enabling hardware below Gen6.

## State and Persistence Behavior
The header owns no state. The implementation initializes and tears down GGTT state through `struct i915_ggtt`.

## Dependencies and Integration Points
It includes `intel_gtt.h` for GGTT types and integrates with the platform selection code in `intel_ggtt.c`. The conditional compilation boundary isolates x86 AGP/intel-gtt dependencies.

## Risks
Using the GMCH backend on non-x86 is intentionally blocked. Prototype or stub return-value changes can break probe fallback behavior in `intel_ggtt.c`.

## Test Signals
Cross-architecture builds and pre-Gen6 x86 probe/enable paths validate the header.
