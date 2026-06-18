# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_load_detect.c

Purpose: provides legacy load-detection pipe allocation for connector probing paths that need to temporarily light up a CRTC at a known mode, then restore the previous atomic state.

Important APIs/types/functions: `intel_load_detect_get_pipe()` finds or allocates a suitable CRTC, commits a 640x480@72Hz load-detect mode, disables affected planes, and returns duplicated restore state. `intel_load_detect_release_pipe()` commits the duplicated state back. `intel_modeset_disable_planes()` adds affected planes to the temporary atomic state and detaches them.

Control flow: callers hold `connection_mutex` and pass an acquire context. If the connector already has a CRTC, that CRTC is used. Otherwise, the first disabled compatible CRTC from the encoder's possible CRTC mask is locked and selected. The function builds two internal atomic states: one for the temporary load-detect commit and one restore snapshot containing connector, CRTC, and affected planes. After committing the temporary state, it waits one vblank before returning the restore state. Release commits the duplicated old state and drops it.

State and persistence behavior: temporary state is internal atomic state. The live hardware CRTC/connector/plane state is changed during detection and restored later. No durable persistence exists.

Dependencies and integration points: depends on DRM atomic helpers, modeset acquire contexts and deadlock handling, i915 CRTC state, connector/encoder attachment, and `intel_crtc_wait_for_next_vblank()`.

Risks: failure returns `ERR_PTR(-EDEADLK)` only for lock backoff and `NULL` for other errors, so callers must distinguish both. If restore commit fails, the temporary mode may remain. Plane disabling avoids stale scanout during load detect but can visibly disturb active outputs if an already assigned CRTC is reused. Correct lock ownership is required by the warning on `connection_mutex`.

Test signals: legacy TV/CRT load detection, no-free-CRTC failure, deadlock retry paths, restoration after successful probe, restoration failure logging, and vblank wait before measurement.
