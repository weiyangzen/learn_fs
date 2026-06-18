# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_core.h

## Purpose
`intel_display_core.h` defines the central `struct intel_display` aggregate and major display subsystem state containers. It is the display driver's in-memory root: platform identification, parent callbacks, hooks, global modeset objects, locks, cached hardware state, power domains, workqueues, VBT data, hotplug state, IRQ masks, watermarks, audio, DPLL, FBC, GMBUS, HDCP, DMC, and restore state all hang from this structure.

## Important APIs, Types, And Functions
Important types include `struct intel_display_funcs`, `struct intel_wm_funcs`, `struct intel_audio_state`, `struct intel_audio`, `struct intel_dpll_global`, `struct intel_frontbuffer_tracking`, `struct intel_hotplug`, `struct intel_vbt_data`, `struct intel_wm`, and `struct intel_display`. The function-pointer tables select platform-specific CRTC enable/disable/readout, watermark, CDCLK, DPLL, hotplug, FDI, color, and audio behavior. Several constants define hardware table sizes such as `I915_NUM_QGV_POINTS` and `I915_NUM_PSF_GV_POINTS`.

## Control Flow And State
This header does not implement control flow, but it encodes synchronization and persistence rules. `display->irq.lock` protects interrupt masks and HPD work enablement; `fb_tracking.lock` protects frontbuffer busy bits; `wm.wm_mutex` protects watermark programming and active watermark state; `dpll.lock` serializes shared PLL programming; mutexes protect GMBUS, HDCP, backlight, PPS, SBI, PM demand, and FBC system-cache state. Restore fields persist suspend/reset modeset state and register shadows. Workqueues split ordered modesets, high-priority flips, cleanup, and unordered display work.

## Dependencies And Integration Points
The structure integrates many display modules: CDCLK, DPLL, FBC, global state, GMBUS, opregion, PCH, power domains, DMC wakelocks, watermark types, DRM connector/modeset locks, and platform info from `intel_display_device.h`. Almost every display implementation file either receives `struct intel_display *` directly or obtains it from a child object.

## Risks And Test Signals
Risks concentrate around lock ordering, lifetime ownership, stale cached hardware state, and teardown ordering of workqueues versus objects they reference. State regressions show up as suspend/resume failures, hotplug storms, watermark corruption, missed vblank/flip events, HDCP/audio races, and use-after-free during driver unload. Test signals include lockdep, KMS suspend/resume, hotplug and MST stress, PSR/FBC tests, runtime PM assertions, debugfs dumps of display info, and CI coverage across old GMCH, PCH-split, and Xe display generations.
