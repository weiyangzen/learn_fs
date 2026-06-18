# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_tv.h

Purpose: declares TV-out initialization for I915 and provides a no-op inline stub for non-I915 builds. This keeps shared display initialization code able to call `intel_tv_init()` without depending on legacy analog TV support.

Important API: `intel_tv_init(struct intel_display *display)` creates the TV encoder and connector when supported and present. The real implementation lives in `intel_tv.c`; the non-I915 stub performs no action.

Control flow and integration: display device initialization can call this function after MMIO and BIOS data are available. The implementation then checks fuses, VBT TV presence, TV DAC sanity, allocates DRM objects, and registers TV connector helpers.

State and persistence: no state in the header. Its compile-time contract determines whether TV-out is possible in a given build. For I915, successful init creates persistent DRM encoder/connector objects and hardware programming paths.

Risks and tests: interface changes affect display initialization. Test signals include I915 builds with TV enabled, non-I915 builds where the inline stub compiles away, and boot paths on machines without TV hardware where the call safely no-ops.
