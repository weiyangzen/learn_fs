# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_overlay.h

## Purpose
Declares the i915 legacy overlay parent interface implementation.

## Important APIs, types, and functions
Exports `i915_display_overlay_interface`.

## Control flow
No runtime flow in the header; display overlay code invokes callbacks through the interface.

## State and persistence
No header state. Implementation stores overlay state in `i915->overlay`.

## Dependencies and integration points
Included by i915 overlay implementation and display glue that consumes `intel_display_overlay_interface`.

## Risks
Interface signature drift is caught at build time.

## Test signals
Build coverage and legacy overlay setup paths.
