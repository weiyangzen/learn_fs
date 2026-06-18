# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_link_bw.h

Purpose: defines the shared-link bandwidth limit structure and exported helpers used by atomic mode computation and connector debugfs.

Important APIs/types/functions: `struct intel_link_bw_limits` holds `link_dsc_pipes`, `bpp_limit_reached_pipes`, and per-pipe `max_bpp_x16` in sixteenth-bpp units. Declarations cover initialization, bpp reduction, simple pipe bpp computation, per-pipe minimum limit setting, atomic shared-link check, and connector debugfs registration.

Control flow: atomic code creates limits, encoder/shared-link checks update them, and `-EAGAIN` asks the caller to recompute CRTC states.

State and persistence behavior: structure instances are transient atomic-check state; debugfs values persist in connector objects.

Dependencies and integration points: depends on `I915_MAX_PIPES`, `enum pipe`, Intel atomic state, CRTC state, and connector types.

Risks: callers must preserve the monotonic decreasing limit invariant and track which pipes have reached minimum bpp.

Test signals: compile coverage, atomic retry behavior, and debugfs availability on DP/eDP/HDMI/VGA/FDI-capable connectors.
