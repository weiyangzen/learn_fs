# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_fbdev_fb.h

Purpose: declares fbdev framebuffer allocation, destruction, pitch alignment, policy, and fb_info filling helpers.

Important APIs/types/functions: `intel_fbdev_fb_pitch_align()`, `intel_fbdev_fb_bo_create()`, `intel_fbdev_fb_bo_destroy()`, `intel_fbdev_fb_fill_info()`, and `intel_fbdev_fb_prefer_stolen()`.

Control flow: no executable code; the header separates low-level backing-object concerns from the main fbdev helper implementation.

State and persistence: no state is owned by the header. The declared functions populate GEM object and fb_info state.

Dependencies and integration: forward-declares DRM device/GEM, fb_info, and i915 VMA types. Used by `intel_fbdev.c`.

Risks: callers must pass a pinned/valid VMA to fill-info and must destroy objects only after failed framebuffer creation or final teardown.

Test signals: compile coverage and fbdev allocation tests that verify each declared helper is available under fbdev emulation builds.
