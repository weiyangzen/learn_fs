# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/oaktrail_crtc.c

## Purpose
This file supplies Oaktrail/Moorestown CRTC helper operations for non-HDMI and HDMI-routed pipes. It computes Oaktrail PLL settings, programs pipe timings and planes, handles DPMS power sequencing, panel fitter decisions, FIFO watermark programming, and framebuffer base updates.

## Important APIs, Types, and Functions
The exported object is `oaktrail_helper_funcs`. Main functions are `oaktrail_crtc_dpms()`, `oaktrail_crtc_mode_set()`, and `oaktrail_pipe_set_base()`. PLL helpers include `mrst_limit()`, `mrst_lvds_clock()`, `mrst_sdvo_find_best_pll()`, and `mrst_lvds_find_best_pll()`. Limit tables encode different LVDS SKU frequencies and SDVO constraints.

## Control Flow
DPMS routes HDMI CRTCs to `oaktrail_crtc_hdmi_dpms()`. For LVDS/SDVO it powers the display, enables or disables DPLL, pipe, and plane registers, waits for vblank/stabilization, and writes fixed FIFO watermark values. Mode set discovers attached encoder type, disables VGA and panel fitter, writes timing registers, handles no-scale centering by adjusting blank/sync windows, calls `mode_set_base()`, computes PLL values from core or SDVO ref clock, writes FP/DPLL/pipe/plane registers across primary and AUX register windows when needed, then releases power.

## State and Persistence Behavior
The file updates CRTC saved modes, hardware timing/PLL/plane registers, and framebuffer base/surface registers. It uses `gma_power_begin()`/`gma_power_end()` for MMIO access. It does not allocate long-lived state, relying on `gma_crtc`, `drm_psb_private.regmap`, and framebuffer GEM offsets.

## Dependencies and Integration Points
It integrates with DRM CRTC helper callbacks, `gma_display` helpers, GEM framebuffer objects, Oaktrail HDMI CRTC helpers, LVDS/SDVO encoder type discovery, and register maps from `oaktrail_device.c`. PLL decisions depend on `dev_priv->core_freq` populated by MID fuse setup.

## Risks
PLL programming depends on SKU-derived core frequency and hardcoded conversion tables; a bad `core_freq` causes wrong clocks. `need_aux` mirrors writes to AUX for SDVO and must align with platform register mapping. DPMS and mode set perform direct register polling with fixed delays. Framebuffer offset programming assumes `to_psb_gem_object(fb->obj[0])->offset` is valid and already bound.

## Test Signals
Test by setting LVDS and SDVO modes at multiple clocks, checking no-scale/aspect/fullscreen behavior, verifying pipe/plane disable/enable sequencing on DPMS, observing stable FIFO watermarks, and confirming framebuffer panning/base updates without corruption or power-management failures.
