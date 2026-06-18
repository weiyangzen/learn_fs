## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce110/dce110_transform_v.c

Purpose: DCE11 underlay transform/scaler implementation. It programs SCLV viewport, overscan, scaling taps, filter coefficients, ratios/inits, line-buffer configuration, gamut no-op, pixel-storage depth, and exposes underlay OPP CSC/regamma callbacks through `transform_funcs`.

Important APIs: `dce110_transform_v_construct`, `dce110_xfmv_set_scaler`, `dce110_xfmv_power_up_line_buffer`, `dce110_xfmv_set_pixel_storage_depth`, and `dce110_xfmv_reset`. Helpers calculate luma/chroma viewport for 4:2:0, choose 64-phase filters, and program coefficient RAM.

Control flow: scaler setup powers line buffer, calculates viewport, writes overscan, configures taps/modes, programs ratios and filter coefficient memories only when coefficients changed, writes viewport, and flips coefficient memory with `SCL_COEF_UPDATE_COMPLETE`. Pixel-depth setup maps LB depth enums to `LBV_DATA_FORMAT` fields.

State and dependencies: state includes cached filter pointers in `dce_transform`, line-buffer metadata, hardware SCLV/LBV registers, and memory power state around coefficient RAM. Dependencies include filter tables, fixed-point conversion, DCE11 registers, and OPP CSC/regamma functions. Risks include hard-coded init values, coefficient-cache pointer comparison, sparse 4:2:0-only chroma handling, unsupported gamut remap, and polling around power gating. Test signals include scaling quality, 4:2:0 viewport correctness, coefficient updates, depth formats, and visual-confirm overscan adjustments.
