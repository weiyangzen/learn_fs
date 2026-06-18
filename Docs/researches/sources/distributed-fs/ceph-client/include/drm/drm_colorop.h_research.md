# sources/distributed-fs/ceph-client/include/drm/drm_colorop.h

## Purpose
This header defines DRM color operation objects used to model per-plane color pipelines. A colorop is a mode object chained through a read-only next pointer and configured through atomic state/properties for curves, LUTs, matrices, multipliers, bypass, and interpolation.

## Important APIs, types, and functions
Important definitions include `DRM_COLOROP_FLAG_ALLOW_BYPASS`, `enum drm_colorop_curve_1d_type`, `struct drm_colorop_state`, `struct drm_colorop_funcs`, and `struct drm_colorop`. Initialization helpers create curve, 1D LUT, 3x4 CTM, multiplier, and 3D LUT operations. Other APIs find, clean up, destroy, duplicate/destroy/reset atomic state, destroy whole pipelines, set next-property links, iterate colorops, and return stable names for types, transfer functions, and interpolation modes.

## Control Flow
Drivers create colorops for a plane, set their supported type/properties, chain them with `drm_colorop_set_next_property`, and expose the pipeline to userspace. Atomic property decoding updates `drm_colorop_state`; plane state can reference a colorop pipeline; check/commit code applies or bypasses operations depending on state and hardware limits.

## State and Persistence
Colorops are persistent DRM mode objects listed in `mode_config.colorop_list`, with invariant indexes and per-plane ownership. Mutable state contains bypass, curve type, multiplier, data blob, and atomic backpointer. Blob data interpretation is type-specific and must survive until state destruction.

## Dependencies and Integration Points
It depends on DRM mode objects, properties, UAPI colorop type enums, planes, atomic state, and property blobs. It integrates with `drm_atomic.h` colorop arrays and the plane color pipeline client capability.

## Risks and Test Signals
Risks include exposing a bypass property that cannot reliably bypass, invalid next-chain topology, blob size/type mismatches, stale blob references after duplicate/destroy, and nonblocking commits reading colorop state without locks. Tests should cover each initializer, state duplicate/destroy with blobs, bypass true fallback, chain ordering and next property IDs, lookup by leased/unleased file, pipeline destruction, and unsupported transfer/interpolation names.
