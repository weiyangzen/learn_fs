<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn10/dcn10_dpp.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn10/dcn10_dpp.c

Purpose: implements the DCN1.0 Display Pipe Processor front-end object: state readback, scaler tap selection, color conversion setup, degamma/regamma control, cursor programming, DPP clock control, function-table registration, and construction.

Important APIs/types/functions: exported functions include `dpp_read_state()`, `dpp1_get_optimal_number_of_taps()`, `dpp_reset()`, `dpp1_cnv_setup()`, `dpp1_set_cursor_attributes()`, `dpp1_set_cursor_position()`, `dpp1_cnv_set_optional_cursor_attributes()`, `dpp1_dppclk_control()`, `dpp_force_disable_cursor()`, and `dpp1_construct()`. Static helpers include `dpp1_cm_set_regamma_pwl()`, `dpp1_setup_format_flags()`, and `dpp1_set_degamma_format_float()`. `dcn10_dpp_funcs` and `dcn10_dpp_cap` publish the implementation through the generic `struct dpp` interface.

Control flow: construction wires context, instance, registers, shifts, masks, caps, and line-buffer constants. Setup maps surface pixel formats to CNVC pixel format codes, alpha behavior, float output, degamma format, default/input CSC selection, and cursor disable requirements for some YCrCb formats. Cursor positioning transforms coordinates for rotation/mirror/hotspot, clips against viewport, and writes enable state unless cursor offload is active. Regamma PWL uses double-buffered LUT RAM selection and skips reprogramming when cached PWL data matches.

State and persistence behavior: caches scaler filters, PWL data, cursor position/attributes, cursor offload, LUT RAM safety toggle, line-buffer caps, and register descriptors in `struct dcn10_dpp`. Hardware register state persists in the DPP block until reprogrammed or reset.

Dependencies and integration points: depends on DC register helper macros, `dcn10_dpp.h`, color-management helpers from DCN10 DPP CM/DSCL files, fixed-point conversion helpers, and generic DPP function-table consumers in AMD DC resource code.

Risks and test signals: format-to-register mappings and cursor rotation math are user-visible. FP16 scaling is rejected on fixed-format DSCL hardware only when both horizontal and vertical ratios differ from one, which should match hardware limits. Regamma cache comparison assumes `pwl_params` is fully initialized. Test signals include format setup for RGB/YUV/FP16, CSC adjustment/default paths, cursor clipping and rotation, regamma LUT A/B toggling, dppclk enable/divider, state readback, and scaler tap defaults with identity-ratio collapse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn10/dcn10_dpp.c -->
