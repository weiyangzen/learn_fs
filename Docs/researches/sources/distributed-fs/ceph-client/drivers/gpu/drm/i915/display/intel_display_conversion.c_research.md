# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_conversion.c

## Purpose
`intel_display_conversion.c` implements the transitional helper that maps a DRM core device pointer to the display subsystem root object. It exists to support the split between i915 and xe style parent devices while display code is being converted toward `struct intel_display`.

## Important APIs, Types, And Functions
The only exported function is `__drm_to_display(struct drm_device *drm)`. It uses `container_of()` to treat the DRM device as part of `struct __intel_generic_device`, then returns that generic wrapper's `display` pointer. The helper relies on `<drm/intel/display_member.h>`, which defines the generic layout and static assertions for the shared `drm_device` and `intel_display *` member offsets.

## Control Flow And State
There is no branching or mutable state. The function is a pure pointer conversion with a strong layout invariant: both `struct drm_i915_private` and `struct xe_device` must embed compatible members at the same relative offsets. If that invariant is broken, the function returns an invalid pointer and all display callers using DRM-to-display conversion become unsafe.

## Dependencies And Integration Points
The helper is declared in `intel_display_conversion.h` and is consumed by code paths that need to obtain `struct intel_display` from DRM objects before direct display ownership has been threaded through. It is part of the display-member compatibility layer shared by i915 and xe.

## Risks And Test Signals
The risk is structural rather than algorithmic: offset drift in parent device structs would create silent memory corruption. The comment points to `INTEL_DISPLAY_MEMBER_STATIC_ASSERT()` as the compile-time guard. Build coverage across both i915 and xe configurations is the main signal. Runtime failures would appear very early as crashes in display init, debugfs, or atomic paths that call `to_intel_display()`/conversion helpers.
