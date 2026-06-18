# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_debugfs.c

## Purpose
`intel_display_debugfs.c` exposes i915 display diagnostics and selected test controls through debugfs. It provides global display capability/state dumps, framebuffer and power-domain views, CRTC/plane/connector descriptions, DPLL and DDB reports, LPSP and MST status, FIFO underrun rearming, connector DSC/FEC overrides, forced joined-pipe controls, and per-CRTC current bpc/pipe files.

## Important APIs, Types, And Functions
Public entry points are `intel_display_debugfs_register()`, `intel_connector_debugfs_add()`, and `intel_crtc_debugfs_add()`. Global show functions include `intel_display_caps()`, `i915_frontbuffer_tracking()`, `i915_sr_status()`, `i915_gem_framebuffer_info()`, `i915_power_domain_info()`, `i915_display_info()`, `i915_shared_dplls_info()`, `i915_ddb_info()`, `i915_lpsp_status()`, and `i915_dp_mst_info()`. Connector controls include `i915_dsc_fec_support`, `i915_dsc_bpc`, `i915_dsc_output_format`, `i915_dsc_fractional_bpp`, `i915_joiner_force_enable`, and `i915_lpsp_capability`. CRTC controls include optional vblank-evasion stats, `i915_current_bpc`, and `i915_pipe`.

## Control Flow And State
Most functions are seq-file show paths that obtain `struct intel_display` from the DRM info node and then lock only the state they inspect. Global display info takes a runtime PM reference and locks all modeset objects while walking CRTCs and connectors. Framebuffer info locks `mode_config.fb_lock`. DPLL and DDB dumps lock modeset state. Writable debugfs files mutate test-only state: DSC force flags in `struct intel_dp`, `connector->force_joined_pipes`, FIFO underrun reporting state, and vblank debug counters. Several writes parse user input through `kstrtobool_from_user()` or `kstrtoint_from_user()`.

## Dependencies And Integration Points
The file integrates DRM debugfs helpers, seq files, connector iteration, DP/MST helpers, HDCP, PSR, FBC, WM, DMC, HPD, GMBUS, PPS, ALPM, link training, link bandwidth, TC, and display power helpers. `intel_display_debugfs_register()` composes global display debugfs setup by delegating to many submodules and then registering display params through `intel_display_debugfs_params()`.

## Risks And Test Signals
Risks include exposing mutable hardware-forcing knobs that are not validated like normal UAPI, lock ordering in show paths, stale connector state if hotplug races with debugfs reads, and writable controls affecting subsequent modesets without explicit rollback. The file correctly ignores debugfs creation failures and returns `-ENODEV` for disconnected or unsupported objects. Test signals include debugfs smoke reads under connected/disconnected states, DSC forced-mode KMS tests, underrun rearm behavior, lockdep with concurrent hotplug/modeset/debugfs access, and CI comparison of `i915_display_info`/DDB/DPLL dumps before and after modesets.
