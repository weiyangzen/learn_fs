# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_gtt_view_types.h

## Purpose
This header defines the compact data structures that describe alternate GTT views of GEM objects: normal, rotated, partial, and remapped. Display and VMA code use these views to bind object memory in layouts suitable for scanout and partial mappings.

## Important APIs, Types, and Functions
Types are `struct intel_remapped_plane_info`, `struct intel_rotation_info`, `struct intel_partial_info`, `struct intel_remapped_info`, `enum i915_gtt_view_type`, and `struct i915_gtt_view`. View type values encode the size of the corresponding payload for rotated, partial, and remapped views.

## Control Flow
There is no executable flow. Callers populate `i915_gtt_view` and pass it to VMA/GGTT pinning and display mapping helpers, which use `type` to interpret the union payload.

## State and Persistence Behavior
View structures are value descriptors. `intel_remapped_plane_info` is packed and uses bitfields to store page offsets and linear-vs-tiled interpretation. No global state is stored here.

## Dependencies and Integration Points
It depends only on Linux integer types. It integrates display plane rotation/remapping, partial object views, and GEM VMA instance lookup, where the view becomes part of the VMA identity.

## Risks
The comments explicitly require no holes/padding in union members. Packing and enum values tied to struct sizes are part of hashing/comparison assumptions in VMA code. Bitfield layout and page-based units must be preserved.

## Test Signals
Display rotation/remapped-plane tests, partial view bindings, VMA view identity tests, static size/layout assertions where available, and modeset/plane updates using rotated framebuffers.
