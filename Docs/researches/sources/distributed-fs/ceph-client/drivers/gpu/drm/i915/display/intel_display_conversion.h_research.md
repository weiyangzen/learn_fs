# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_conversion.h

## Purpose
`intel_display_conversion.h` declares transitional DRM-to-display conversion helpers. It intentionally stays small because it bridges two ownership models rather than defining permanent display policy.

## Important APIs, Types, And Functions
The header forward declares `struct drm_device` and `struct intel_display`, then declares `struct intel_display *__drm_to_display(struct drm_device *drm)`. Include guards prevent duplicate declarations. No inline logic, macros, or state definitions live here.

## Control Flow And State
There is no control flow or persistent state in the header. Its behavioral contract is delegated to `intel_display_conversion.c`: callers passing a valid DRM device associated with an i915/xe generic display parent receive the associated `intel_display`.

## Dependencies And Integration Points
The header is used by display code that cannot yet include heavier internal structures or that needs a neutral conversion API during display-core migration. Its minimal forward declarations reduce include coupling and make it suitable for broad inclusion.

## Risks And Test Signals
Risk is mainly API misuse: calling the helper for a DRM device that does not satisfy the shared layout contract is invalid. Build tests catch declaration mismatches; runtime KMS probe and debugfs access catch bad conversions. Long term, this file should shrink or disappear as direct `struct intel_display *` plumbing replaces conversion calls.
