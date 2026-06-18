# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_cursor.h

Purpose: declares the cursor plane module interface used by display initialization and vblank work plumbing.

Important APIs: `intel_cursor_plane_create(struct intel_display *display, enum pipe pipe)` creates one DRM universal cursor plane for a pipe. `intel_cursor_unpin_work(struct kthread_work *base)` is the vblank work callback that unpins and destroys retired cursor plane state. `intel_cursor_mode_config_init(struct intel_display *display)` sets mode-config cursor dimensions based on platform.

Control flow and state: no direct behavior or state; it exposes functions implemented in `intel_cursor.c`. Forward declarations keep include dependencies small for `enum pipe`, `struct intel_display`, `struct intel_plane`, and `struct kthread_work`.

Dependencies and integration: used by CRTC construction, display driver mode-config initialization, and vblank work scheduling. Its functions bridge DRM plane creation with i915 cursor-specific callbacks.

Risks: callers must respect that created planes have platform-specific validation and programming callbacks. The unpin work callback expects `base` to be embedded in an `intel_plane_state` as initialized by cursor update code.

Test signals: build coverage from display initialization and runtime validation that every pipe gets a cursor plane with expected cursor size limits.
