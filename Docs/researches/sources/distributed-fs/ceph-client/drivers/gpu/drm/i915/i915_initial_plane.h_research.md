# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_initial_plane.h

## Purpose
Declares the i915 implementation of the display initial-plane parent interface.

## Important APIs, types, and functions
Exports `i915_display_initial_plane_interface`, a `struct intel_display_initial_plane_interface` implemented in `i915_initial_plane.c`.

## Control flow
No runtime flow exists in the header. Consumers call through the interface table to allocate, set up, wait, and clean up initial plane resources.

## State and persistence
No local state. Interface callbacks manipulate `intel_initial_plane_config`, GEM objects, and VMA references in the implementation.

## Dependencies and integration points
Used by display code that is decoupled from i915-specific GEM details through `display_parent_interface`.

## Risks
Signature drift between the display parent interface and this extern would be caught at build/link time.

## Test signals
Build coverage and boot display takeover paths validate the declaration.
