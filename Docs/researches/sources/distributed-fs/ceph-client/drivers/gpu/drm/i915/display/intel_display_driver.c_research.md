# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_driver.c

## Purpose
`intel_display_driver.c` provides high-level display lifecycle entry points between the parent i915/xe driver and lower-level display modules. It sequences probe, registration, user access gating, suspend/resume, and removal without embedding detailed per-platform programming.

## Important APIs, Types, And Functions
Public functions include `intel_display_driver_probe_defer()`, `intel_display_driver_init_hw()`, `intel_display_driver_early_probe()`, `intel_display_driver_probe_noirq()`, `intel_display_driver_probe_nogem()`, `intel_display_driver_probe()`, `intel_display_driver_register()`, remove/unregister variants, suspend/resume functions, and display access controls. Static helpers define DRM mode config callbacks (`intel_mode_funcs`, `intel_mode_config_funcs`), initialize/cleanup mode config, set plane possible CRTCs, and set/check access state.

## Control Flow And State
Probe is split into ordered phases. Early probe detects PCH, initializes locks and hooks. `probe_noirq()` initializes vblank, BIOS, PSR workarounds, power domains, PM demand, workqueues, DMC, mode config, CDCLK, color, DBUF, bandwidth, quirks, and FBC. `probe_nogem()` initializes WM, panel SSC, PPS, GMBUS, CRTCs, DPLLs, hardware state, outputs, DP tunnel manager, disables user access, reads current modeset state, and sanitizes watermarks. `probe()` runs post-GEM work: HDCP component, flip queue, initial commit, overlay, HPD, and IPC watermarks. Registration enables VGA/opregion/ACPI/audio/debugfs/fbdev and user access. Teardown and unregister reverse these layers and flush workqueues.

## Dependencies And Integration Points
The file orchestrates nearly every display submodule: BIOS/VBT, power domains, DMC, PM demand, CRTC/plane, CDCLK, color, DBUF, BW, DPLL, FDI, outputs, DP tunnel/MST, HDCP, flipq, overlay, HPD, watermark, VGA, opregion, ACPI, audio, fbdev, and debugfs. DRM atomic helper callbacks bind i915 display operations into the DRM core.

## Risks And Test Signals
Risks are ordering bugs, partial-probe cleanup leaks, workqueue lifetime races, and user access opening before hardware state is safe. Access gating is important during load/unload/suspend to prevent user modesets and connector probes from touching hardware at unsafe times. Test signals include probe error injection, boot on no-display and fused-off devices, suspend/resume/hibernate, driver unload/reload, MST suspend/resume, hotplug after fbdev setup, lockdep during access transitions, and initial commit failures logged without breaking driver load.
