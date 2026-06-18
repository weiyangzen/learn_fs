# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn10/dcn10_dpp_cm.c

## Purpose
`dcn10_dpp_cm.c` implements DCN 1.0 DPP color-management programming. It handles gamut remap, input and output CSC, regamma and degamma piecewise-linear LUTs, input gamma LUT, bias/scale, CM bypass, and HDR multiplier programming through the DCN10 register tables.

## Important APIs, types, and functions
- Gamut APIs are `dpp1_cm_set_gamut_remap()` and `dpp1_cm_get_gamut_remap()`, backed by `program_gamut_remap()` and `read_gamut_remap()`.
- Output CSC APIs are `dpp1_cm_set_output_csc_default()` and `dpp1_cm_set_output_csc_adjustment()`, backed by `dpp1_cm_program_color_matrix()`.
- Regamma APIs include `dpp1_cm_power_on_regamma_lut()`, `dpp1_cm_configure_regamma_lut()`, `dpp1_cm_program_regamma_lut()`, `dpp1_cm_program_regamma_luta_settings()`, and `dpp1_cm_program_regamma_lutb_settings()`.
- Degamma APIs include `dpp1_power_on_degamma_lut()`, `dpp1_set_degamma()`, `dpp1_set_degamma_pwl()`, `dpp1_degamma_ram_select()`, `dpp1_program_degamma_lut()`, and the RAM A/B settings helpers.
- `dpp1_program_input_csc()`, `dpp1_program_bias_and_scale()`, `dpp1_program_input_lut()`, `dpp1_full_bypass()`, and `dpp1_set_hdr_multiplier()` cover the remaining CM integration points.
- The file depends heavily on `cm_helper_program_color_matrices()`, `cm_helper_read_color_matrices()`, `cm_helper_program_xfer_func()`, `convert_float_matrix()`, `convert_hw_matrix()`, and `find_color_matrix()`.

## Control flow
Gamut remap starts by bypassing when the adjustment is not software-controlled. For software matrices it converts twelve fixed-point matrix entries to hardware register values, programs either the main gamut registers or COMA/COMB registers, and then sets `CM_GAMUT_REMAP_MODE`. Readback performs the inverse by reading the active mode and matrix bank, then converting register values back to fixed-point.

Output CSC uses a double-buffer pattern. `dpp1_cm_program_color_matrix()` reads CM debug status index 9 to see which output CSC path is active, programs the alternate OCSC/COMB matrix register bank, then switches `CM_OCSC_MODE`. Input CSC follows the same idea with ICSC/COMA selection in `dpp1_program_input_csc()`, using either a default matrix from `dpp_input_csc_matrix` or a caller-provided `out_csc_color_matrix`.

Regamma and degamma PWL programming split metadata and LUT payload. The settings functions map `struct pwl_params` into per-channel start/slope/end/region registers through `xfer_func_reg`; the payload functions stream red/green/blue base and delta values into LUT data registers. `dpp1_set_degamma_pwl()` detects the currently used RAM, programs the inactive RAM, writes the payload, and flips the selected LUT mode. Input gamma writes a 256-entry LUT into the inactive IGAM RAM and then enables that RAM.

## State and persistence behavior
Runtime state is stored in hardware registers and in the DPP object only indirectly. The file reads hardware status fields to decide which double-buffered bank is active, then writes the inactive bank to avoid visible mid-frame updates. `CM_MEM_PWR_CTRL` controls LUT memory power. `dpp1_program_input_lut()` temporarily powers shared memory, writes the selected IGAM RAM, powers memory back down, and changes `CM_IGAM_LUT_MODE`. There is no durable persistence.

## Dependencies and integration points
The implementation integrates with the generic `struct dpp_funcs` entries declared in `dcn10_dpp.h` and installed by `dcn10_dpp.c`. It depends on `reg_helper.h` register access macros, `dcn10_cm_common.h` color matrices and helper structures, fixed-point conversion helpers, display debug flags, and the display core color types (`dc_gamma`, `pwl_params`, `dpp_grph_csc_adjustment`, `dc_bias_and_scale`).

## Risks and edge cases
Double-buffer selection depends on debug/status register encodings. If those encodings differ across ASIC revisions or masks are wrong, the driver can overwrite the active bank or switch to an unprogrammed bank. Several invalid inputs trigger `BREAK_TO_DEBUGGER()` rather than graceful fallback. `dpp1_program_input_lut()` assumes the gamma object has a suitable number of entries for the 256-entry IGAM path and warns in comments that values beyond 8 bits per channel are truncated. Power-control semantics are subtle: `SHARED_MEM_PWR_DIS` is written with different values depending on whether memory should be accessible or disabled.

## Test signals
Test signals include CSC/gamut matrix programming with readback, rapid color-space changes while scanning out, PWL degamma/regamma transitions between RAM A and RAM B, bypass and hardware sRGB/xvYCC degamma modes, 256-entry input gamma programming, HDR multiplier changes, CM bypass toggling, register traces around memory power transitions, and visual/CRC tests for YCbCr and RGB conversion paths.
