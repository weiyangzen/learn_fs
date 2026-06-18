# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_panic.h

## Purpose
Declares the i915 DRM panic parent interface.

## Important APIs, types, and functions
Exports `i915_display_panic_interface`.

## Control flow
No runtime flow in the header.

## State and persistence
No state.

## Dependencies and integration points
Included by display panic glue and implementation code.

## Risks
Only interface signature drift risk.

## Test signals
Build coverage and DRM panic setup on i915.
