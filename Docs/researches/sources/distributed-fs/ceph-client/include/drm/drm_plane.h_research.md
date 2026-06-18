# sources/distributed-fs/ceph-client/include/drm/drm_plane.h

## Purpose
`drm_plane.h` declares the central KMS plane object and its mutable state. Planes represent scanout hardware that samples a framebuffer, applies positioning, scaling, blending, color conversion, and damage tracking, then feeds pixels to a CRTC.

## Important APIs, types, and functions
Key types are `struct drm_plane_state`, `struct drm_plane_funcs`, `enum drm_plane_type`, and `struct drm_plane`. State fields include CRTC/framebuffer/fence links, source and destination rectangles, cursor hotspot, alpha, blend mode, rotation, zpos, color encoding/range, damage clips, scaling filter, color pipeline, commit, and color-management change flags. Driver hooks cover legacy update/disable, cleanup/reset, legacy and atomic properties, atomic state duplication/destruction/printing, late/early userspace registration, and format/modifier support. APIs include `drm_universal_plane_init`, `drmm_universal_plane_alloc`, `drm_universal_plane_alloc`, `drm_plane_cleanup`, `drm_plane_find`, `drm_plane_has_format`, damage helpers, scaling filter property creation, size hints, and color pipeline property creation.

## Control flow
Drivers create planes with supported formats/modifiers and possible CRTC masks. Legacy paths use `update_plane` and `disable_plane`; atomic drivers duplicate state, set properties into the pending state, validate in atomic check, and commit prepared state to hardware. Iteration macros traverse all planes, legacy overlay-only planes, or masked plane sets. Damage blobs and derived `src` / `dst` rectangles are consumed by atomic helpers and drivers.

## State and persistence
Plane objects are registered for the DRM device lifetime; mutable atomic state is protected by the plane modeset lock and commit ordering. Non-atomic `crtc`, `fb`, and `old_fb` fields remain only for legacy drivers. Property pointers persist after creation. There is no storage persistence.

## Dependencies and integration points
The header depends on DRM mode objects, rectangles, color management, modeset locks, framebuffers, dma-fence, kmsg panic dump registration, atomic state, and CRTC/connector integration. It is used by virtually all KMS display drivers and helpers.

## Risks and test signals
Risks include direct mutation of state fields instead of atomic setters, stale fence/framebuffer references during nonblocking commits, incorrect format/modifier filtering, bad zpos normalization, damage clip coordinate mistakes, cursor hotspot property mishandling, panic dumper lifetime issues, and legacy/atomic semantic mismatches. Test signals include atomic plane update/disable, universal plane enumeration, modifier validation, damage tracking, zpos conflicts, color properties, cursor planes, nonblocking commit teardown, and KMS plane selftests.
