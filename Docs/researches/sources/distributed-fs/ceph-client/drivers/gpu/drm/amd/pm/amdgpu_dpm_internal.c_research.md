# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/amdgpu_dpm_internal.c

## Purpose
`amdgpu_dpm_internal.c` contains an internal helper, `amdgpu_dpm_get_display_cfg`, that snapshots active DRM display configuration into `adev->pm.pm_display_cfg` for use by PM backends. It derives active display count, pixel clocks, minimum vblank time, first active refresh rate, selected CRTC index, line time, and default display clock.

## Important APIs and Data
The sole exported function in this file is `amdgpu_dpm_get_display_cfg(struct amdgpu_device *adev)`. It uses `adev_to_drm`, `struct amd_pp_display_configuration`, `struct single_display_configuration`, DRM CRTC lists, `struct amdgpu_crtc`, and `struct amdgpu_connector`. It writes `cfg->min_vblank_time`, `cfg->vrefresh`, `cfg->crtc_index`, `cfg->line_time_in_us`, per-display `controller_id` and `pixel_clock`, `cfg->display_clk`, and `cfg->num_display`.

## Control Flow and State
The helper initializes `min_vblank_time` to `0xffffffff`, then only scans CRTCs when CRTC support exists and mode configuration has been initialized. It skips disabled CRTCs, converts each active DRM CRTC to AMDGPU types, records one display entry, and computes refresh/vblank timing when `hw_mode.clock` is non-zero. For refresh rates above 120 Hz on the legacy non-DC path, it forces `vblank_time_us` to zero to disable memory-clock switching. It tracks the lowest vblank time and first active refresh rate, selects the lowest CRTC id as `crtc_index`, records its line time, and finally stores the default display clock and active display count.

The function mutates only `adev->pm.pm_display_cfg`. It does not take `adev->pm.mutex` or DRM mode locks itself, so callers must invoke it from a context where display state is stable enough for PM consumption.

## Dependencies and Integration Points
Includes cover core AMDGPU, display, PowerPlay manager, SW SMU, and the internal DPM header. The function integrates display mode state with PM clock-selection logic, especially memory-clock switching decisions and backend display-configuration-change hooks. It depends on active CRTCs having a valid `connector` pointer and usable `pixelclock_for_modeset`.

## Risks
The active-display array is filled by incrementing `num_crtcs`; safety depends on the array being sized for the maximum possible active displays. Missing locking can be risky if callers use it during concurrent modeset changes. The high-refresh workaround intentionally disables mclk switching above 120 Hz on legacy paths; removing it could reintroduce display instability. Calculating vblank time from mode totals assumes sane mode fields and non-zero clock.

## Test Signals
Useful tests include display hotplug and modeset changes, multiple active CRTCs, high-refresh modes above 120 Hz, zero-clock or disabled CRTC cases, suspend/resume, and PM clock changes after display reconfiguration. Runtime validation should inspect `pm_display_cfg` consumers for correct display count, min vblank, refresh, CRTC index, line time, and pixel clock values.
