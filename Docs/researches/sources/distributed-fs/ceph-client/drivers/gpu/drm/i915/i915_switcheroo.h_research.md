<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_switcheroo.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_switcheroo.h

## Purpose
Declares i915 VGA switcheroo registration helpers.

## Important APIs, types, and functions
- Forward declares `struct drm_i915_private`.
- Exports `i915_switcheroo_register()` and `i915_switcheroo_unregister()`.

## Control flow
No runtime control flow exists in the header. It exposes a narrow API to driver load/unload code.

## State and persistence
No state is stored here. Registration state is owned by VGA switcheroo and the implementation.

## Dependencies and integration points
Included by i915 driver initialization/cleanup code and implemented by `i915_switcheroo.c`.

## Risks
The include guard lacks a trailing `_H` style suffix but is internally consistent. API expansion should remain minimal because switcheroo policy is implementation-local.

## Test signals
Build coverage and successful switcheroo register/unregister during driver probe/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_switcheroo.h -->
