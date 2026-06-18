# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_initial_plane.h

Purpose: declares initial plane takeover helpers.

Important APIs/types/functions: `intel_initial_plane_config()` reconstructs active primary plane state, and `intel_initial_plane_vblank_wait()` waits for a vblank through the display parent interface.

Control flow: display initialization calls `intel_initial_plane_config()` after CRTC/plane hardware readout is available.

State and persistence behavior: no state in the header; implementation mutates CRTC primary plane state and framebuffer references.

Dependencies and integration points: connects display initialization to platform-specific initial-plane callbacks and `struct intel_crtc`.

Risks: callers must only invoke this after display objects and platform hooks are initialized.

Test signals: build coverage and driver takeover with BIOS primary planes active.
