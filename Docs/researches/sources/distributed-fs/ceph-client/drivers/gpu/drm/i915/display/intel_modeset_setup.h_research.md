# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_modeset_setup.h

Purpose: declares the modeset hardware-state setup entry point. It forward declares `struct drm_modeset_acquire_ctx` and `struct intel_display` to keep include dependencies small.

Important API: `void intel_modeset_setup_hw_state(struct intel_display *display, struct drm_modeset_acquire_ctx *ctx);` imports current hardware state, sanitizes it, and updates the driver's display state model.

Control flow/state: this header has no runtime state; callers supply a display object and an already relevant modeset acquire context used by the implementation when disabling inherited/broken CRTCs without going through a normal atomic userspace commit.

Dependencies/integration: consumed by display init/resume code that must reconcile firmware-programmed state before normal atomic commits and verification can run.

Risks/test signals: signature changes ripple into display bring-up. Build coverage across i915 and non-i915 display builds is the main header-level signal.
