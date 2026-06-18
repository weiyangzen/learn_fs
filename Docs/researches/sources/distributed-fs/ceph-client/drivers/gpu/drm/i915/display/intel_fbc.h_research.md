# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_fbc.h

Purpose: declares the i915 FBC interface consumed by display atomic, plane, frontbuffer, FIFO underrun, dirty-rect, debugfs, and init/cleanup code. It hides the internal `struct intel_fbc` implementation while exposing lifecycle and update hooks.

Important APIs/types/functions: defines `enum intel_fbc_id` for FBC instances A-D and `I915_MAX_FBCS`. Declares `intel_fbc_atomic_check()`, `intel_fbc_min_cdclk()`, `intel_fbc_pre_update()`, `intel_fbc_post_update()`, `intel_fbc_update()`, `intel_fbc_disable()`, `intel_fbc_init()`, `intel_fbc_cleanup()`, `intel_fbc_sanitize()`, frontbuffer callbacks, underrun handlers, debugfs helpers, dirty-rect helpers, `intel_fbc_add_plane()`, and `intel_fbc_need_pixel_normalizer()`.

Control flow: no executable code is defined here; the header documents the call surface. Atomic modeset code calls check/pre/update/post/disable hooks, frontbuffer code calls invalidate/flush, underrun IRQ code calls handler/reset/read-debug helpers, and plane setup links planes to FBC instances.

State and persistence: declares opaque state only. Persistent data is owned by `intel_fbc.c` and `struct intel_display`.

Dependencies and integration: forward-declares i915 display types and `enum fb_op_origin`; consumers include display core, frontbuffer tracking, CRTC debugfs, FIFO underrun, and plane initialization.

Risks: the interface has ordering assumptions not encoded in the header: atomic check must precede update, pre/post update bracket plane register changes, and underrun handling may asynchronously disable active FBC. Misusing these hooks can leave stale compression state or lost frontbuffer invalidations.

Test signals: build coverage with FBC enabled/disabled in config and module params; modeset paths should link against all declared hooks and exercise check/pre/post/update ordering through atomic display tests.
