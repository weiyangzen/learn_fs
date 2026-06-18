<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/cdv_intel_dp.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/cdv_intel_dp.c

## Purpose

This file implements Cedarview DisplayPort and embedded DisplayPort support. It includes a legacy I2C-over-AUX adapter, native AUX helpers, DPCD and EDID probing, link bandwidth/lane selection, M/N ratio programming, eDP panel power and backlight sequencing, port mode programming, sink power management, and two-phase DP link training.

## Important APIs, Types, And Functions

The exported entry points are `cdv_intel_dp_init()` and `cdv_intel_dp_set_m_n()`. Important local types are `struct i2c_algo_dp_aux_data`, `struct cdv_intel_dp`, `struct ddi_regoff`, and `struct cdv_intel_dp_m_n`. Important functions include AUX/I2C helpers (`cdv_intel_dp_aux_ch()`, native read/write, I2C xfer), eDP helpers (`cdv_intel_edp_panel_vdd_on/off()`, `panel_on/off()`, `backlight_on/off()`), mode helpers (`cdv_intel_dp_mode_valid()`, `mode_fixup()`, `mode_set()`), training helpers (`cdv_intel_dp_start_link_train()`, `complete_link_train()`, `link_down()`), detect/get_modes/property callbacks, `cdv_intel_dpc_is_edp()`, and `cdv_disable_intel_clock_gating()`.

## Control Flow

Initialization allocates encoder/connector/private state, chooses DisplayPort versus eDP using VBT child-device data, initializes DRM objects, sets output type and DDI selection for DP_B or DP_C, disables display clock gating needed for DP/eDP bring-up, creates an AUX-backed I2C adapter, attaches force-audio and broadcast-RGB properties, and for eDP reads panel timing delays from panel-power registers and validates DPCD while VDD is forced on. Detection reads DPCD over native AUX, optionally reads EDID for audio, and toggles eDP VDD around AUX access. Mode fixup chooses link bandwidth and lane count sufficient for pixel clock and bpp, using a forced maximum fallback for eDP. Commit powers the panel, performs pattern 1 clock recovery and pattern 2 channel equalization with AUX status feedback, then enables backlight.

## State And Persistence

`struct cdv_intel_dp` stores the output register, pending DP register image, link configuration, DPCD, train set/status, audio/color properties, AUX adapter state, lane count/link bandwidth, and eDP power delays/fixed mode/panel-on state. Hardware state persists in DP_B/DP_C registers, AUX control/data registers, DPCD sink registers, PP_CONTROL/status/delay registers, BLC PWM routing, pipe M/N registers, and DPIO lane training registers.

## Dependencies And Integration Points

The file depends on DRM DP helper constants, DRM EDID helpers, I2C core, shared GMA display helpers, `cdv_sb_write()` sideband support, GMA backlight, VBT child device fields from `intel_bios.h`, and Cedarview CRTC mode-set which calls `cdv_intel_dp_set_m_n()`.

## Risks And Test Signals

Risks include the legacy AUX helper needing migration, busy-wait AUX loops without an explicit timeout inside the send-busy wait, complex eDP power sequencing, partial cleanup on DP init failures, disabled DPIO training code under `CDV_FAST_LINK_TRAIN`, property changes forcing full modesets, and link-training fallback behavior that may leave a marginal link active. Test signals are DP/eDP detection, DPCD reads, EDID-over-AUX, force-audio and broadcast-RGB property changes, 1/2/4 lane training at 1.62 and 2.7 Gbps, eDP VDD/panel/backlight timing, hotplug, suspend/resume, and AUX timeout/error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/cdv_intel_dp.c -->
