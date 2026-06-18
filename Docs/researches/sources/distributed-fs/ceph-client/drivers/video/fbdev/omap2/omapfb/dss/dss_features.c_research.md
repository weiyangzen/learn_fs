# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/dss_features.c

## Purpose

This file is the OMAP DSS SoC capability database. It records register field layouts, supported feature flags, manager/overlay counts, display/output matrices, color modes, overlay capabilities, clock-source names, numeric limits, rotation support, and FIFO units for OMAP2, OMAP3, AM35xx, AM43xx, OMAP4, OMAP5, and DRA7-class DSS variants. The complete 940-line source was read.

## Important APIs, Types, and Functions

Private types are `struct dss_reg_field`, `struct dss_param_range`, and `struct omap_dss_features`. Static tables cover feature ids, register fields, supported displays/outputs, supported color modes, overlay capabilities, clock-source names, parameter ranges, and per-SoC `omap_dss_features` instances.

The public query functions are `dss_feat_get_num_mgrs()`, `dss_feat_get_num_ovls()`, `dss_feat_get_param_min()`, `dss_feat_get_param_max()`, `dss_feat_get_supported_displays()`, `dss_feat_get_supported_outputs()`, `dss_feat_get_supported_color_modes()`, `dss_feat_get_overlay_caps()`, `dss_feat_color_mode_supported()`, `dss_feat_get_clk_source_name()`, `dss_feat_get_buffer_size_unit()`, `dss_feat_get_burst_size_unit()`, `dss_has_feature()`, `dss_feat_get_reg_field()`, `dss_feat_rotation_type_supported()`, and `dss_features_init()`.

## Control Flow

Early DSS initialization calls `dss_features_init(version)`, which selects one static feature table into `omap_current_dss_features`. All later query functions dereference that selected table directly. Feature presence is tested by linear search through the selected feature-id array; register-field queries bounds-check with `BUG_ON`; display/output/color/capability queries index arrays by channel or plane.

## State and Persistence Behavior

The only mutable state is the static pointer `omap_current_dss_features`. All feature data is compile-time constant. There is no file-backed persistence and no runtime mutation of the capability tables after initialization.

## Dependencies and Integration Points

This file depends on OMAP DSS public enums/types and the internal feature enum declarations in `dss_features.h`. It feeds constraints into DSS core clock setup, DISPC overlay validation and FIFO programming, DSI/DPI clock calculations, HDMI audio/CTS feature checks, VENC quirks, and rotation/scaling/format capability checks exposed to upper display layers.

## Risks and Edge Cases

All query functions assume `dss_features_init()` was called with a supported version. Unsupported versions leave the pointer unset after only logging a warning, which would make later queries unsafe. DRA7 maps to the OMAP5 capability table here, while `dss.c` has a separate DRA7 port/clock feature table; keeping those aligned is important. Array sizes must match enum channel/plane indexes used elsewhere. Feature-list omissions can silently disable hardware paths such as HDMI audio MCLK, DSI PHY DCC, MFLAG, or DPI regulator handling.

## Test Signals

Validation includes booting each supported SoC version and checking manager/overlay counts, display/output masks, color mode acceptance/rejection, scaler/downscale and line-width limits, FIFO units, rotation support, clock-source names in debugfs, and feature-gated paths such as LCD clock source selection, DSI VC OCP width, HDMI CTS software mode, and AM35xx/AM43xx regulator differences.
