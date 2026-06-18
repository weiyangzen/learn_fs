# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_sprite_uapi.c

Purpose: implements the legacy `DRM_IOCTL_I915_SET_SPRITE_COLORKEY` path. It translates a userspace `drm_intel_sprite_colorkey` request into atomic plane state updates for overlay planes and, on newer hardware, the relevant primary plane.

Important functions: `intel_sprite_set_colorkey_ioctl()` validates flags, locates the requested DRM overlay plane, builds an internal atomic state, updates color-key fields, and commits it with deadlock retry. `intel_plane_set_ckey()` copies the requested key into `intel_plane_state::ckey` and masks unsupported placement. `has_dst_key_in_primary_plane()` currently returns true for display version 9 and newer.

Control flow: the ioctl clears the no-op `I915_SET_COLORKEY_NONE` bit, rejects unknown flags and simultaneous source/destination keying, rejects destination keying on VLV/CHV, rejects non-overlay or missing planes, and rejects SKL+ destination keying on plane 3 or later. It then obtains the overlay plane state and optionally the primary plane state for the same pipe, calls `intel_plane_set_ckey()` on each, and commits atomically, backing off on `-EDEADLK`.

State and persistence: the persistent software state is `plane_state->ckey`; hardware programming happens later in the plane update callbacks in `intel_sprite.c` and primary-plane code. On SKL+ destination keying is stored on the primary and cleared on sprite planes; source keying is stored on sprites and cleared on primary planes.

Dependencies and tests: depends on DRM plane lookup, modeset acquire contexts, atomic state helpers, `intel_crtc_for_pipe()`, and display version/platform data. Test signals include invalid flag rejection, source vs destination exclusivity, VLV/CHV destination-key rejection, SKL+ plane restrictions, primary-plane companion updates, atomic deadlock retry, and visual colorkey behavior. Risks include legacy UAPI compatibility and mismatched software placement versus hardware programming.
