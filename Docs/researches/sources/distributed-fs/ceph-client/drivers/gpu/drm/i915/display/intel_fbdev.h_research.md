# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_fbdev.h

Purpose: declares the i915 fbdev emulation interface and provides no-op stubs when `CONFIG_DRM_FBDEV_EMULATION` is disabled.

Important APIs/types/functions: exposes `INTEL_FBDEV_DRIVER_OPS`, `intel_fbdev_driver_fbdev_probe()`, `intel_fbdev_setup()`, `intel_fbdev_framebuffer()`, `intel_fbdev_vma_pointer()`, and `intel_fbdev_get_map()` under fbdev emulation. The disabled path maps driver ops to `.fbdev_probe = NULL` and returns harmless defaults.

Control flow: no runtime flow beyond inline stubs. Driver registration uses `INTEL_FBDEV_DRIVER_OPS`; display initialization calls `intel_fbdev_setup()` only if the feature is compiled in.

State and persistence: no state is defined here. Opaque `struct intel_fbdev` state is owned by `intel_fbdev.c`.

Dependencies and integration: forward-declares DRM fb helper, i915 display/framebuffer, and `iosys_map` types. It is consumed by driver setup, display code, and callers that need the fbdev framebuffer/VMA mapping.

Risks: call sites must tolerate NULL framebuffer/VMA when fbdev is disabled or setup failed. The macro-based driver op must stay synchronized with DRM helper expectations.

Test signals: compile with and without `CONFIG_DRM_FBDEV_EMULATION`; verify non-fbdev builds link cleanly and fbdev-enabled builds register the probe callback.
