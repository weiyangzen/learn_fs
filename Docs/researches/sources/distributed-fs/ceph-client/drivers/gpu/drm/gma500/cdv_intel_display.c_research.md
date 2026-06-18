<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/cdv_intel_display.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/cdv_intel_display.c

## Purpose

This file implements Cedarview CRTC mode-setting, DPLL programming through the sideband/DPIO bus, clock limit selection, DisplayPort M/N handoff integration, watermark/self-refresh handling, and current-mode reconstruction for GMA500.

## Important APIs, Types, And Functions

Exported symbols are `cdv_sb_read()`, `cdv_sb_write()`, `cdv_sb_reset()`, `cdv_disable_sr()`, `cdv_update_wm()`, `cdv_intel_crtc_mode_get()`, `cdv_intel_helper_funcs`, and `cdv_clock_funcs`. Important internals include the `cdv_intel_limits[]` table, `cdv_dpll_set_clock_cdv()`, `cdv_intel_limit()`, `cdv_intel_clock()`, `cdv_intel_find_dp_pll()`, `cdv_intel_pipe_enabled()`, `cdv_intel_panel_fitter_pipe()`, `cdv_intel_crtc_mode_set()`, `i8xx_clock()`, and `cdv_intel_crtc_clock_get()`.

## Control Flow

Mode set identifies the active connector type for the CRTC, chooses the reference clock from SKU flags, output type, and LVDS SSC settings, selects a clock limit table, computes PLL divisors, programs DP M/N registers for DP/eDP or clears them for non-DP, configures BPC and plane control, writes the DPLL control register in sync-lock mode, programs DPIO sideband PLL M/N/P/reference/lane registers, handles LVDS pair power before DPLL enable, disables panel fitter if already assigned to this pipe, waits for DPLL lock, writes timing registers, enables pipe/plane, and delegates framebuffer base programming to `gma_pipe_set_base()`. Watermark updates choose single-pipe self-refresh values or dual-pipe suggested values and disable self-refresh as needed.

## State And Persistence

Hardware state persists in DPLL control/MD registers, sideband DPIO registers, lane PLL selection registers, pipe timing/source registers, plane control, panel fitter, watermark registers, self-refresh control, and DP M/N registers. Software state uses `gma_crtc->clock_funcs`, `gma_crtc->pipe`, `gma_crtc->active`, `dev_priv->dplla_96mhz`, `lvds_use_ssc`, `lvds_ssc_freq`, and saved register snapshots when power is unavailable.

## Dependencies And Integration Points

The file integrates DRM CRTC helpers, shared GMA display helpers, Cedarview output types, DP M/N programming from `cdv_intel_dp.c`, power management via `gma_power_begin()`, and `psb_ops` watermark/self-refresh callbacks.

## Risks And Test Signals

Risks include fragile sideband timeouts, hardcoded BIOS-like magic values, incorrect reference clock selection for unusual boards, DPLL lock failures, panel fitter reassignment, self-refresh watermark regressions, and mixed legacy helper return semantics where some failures return zero. Test signals are mode-setting on CRT/HDMI/LVDS/DP/eDP, 27/96/100 MHz refclk platforms, DPLL lock readback, DP link clock modes, single- versus dual-pipe watermarks, suspend/resume mode reconstruction, and display underrun monitoring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/cdv_intel_display.c -->
