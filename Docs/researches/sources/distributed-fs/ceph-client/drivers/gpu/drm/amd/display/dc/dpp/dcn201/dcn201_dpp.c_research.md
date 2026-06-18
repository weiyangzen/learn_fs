# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn201/dcn201_dpp.c

## Purpose
`dcn201_dpp.c` implements the DCN 2.0.1 DPP variant. It largely reuses DCN10 scaler/CSC helpers and DCN20 blend/shaper/3D LUT helpers, while providing DCN201-specific converter setup, tap-selection policy, function table, caps, and constructor.

## Important APIs, types, and functions
- The exported constructor is `dpp201_construct()`.
- `dpp201_cnv_setup()` programs pixel-format conversion, default format-control fields, alpha enablement, two-bit alpha LUT, input CSC selection, cursor disable, and OBUF power.
- `dpp201_get_optimal_number_of_taps()` selects scaler tap counts and rejects unsupported scaling cases.
- The static `dcn201_dpp_funcs` table binds the generation to shared callbacks including `dpp20_read_state()`, `dpp1_dscl_set_scaler_manual_scale()`, `dpp1_cm_set_gamut_remap()`, `dpp2_set_degamma_pwl()`, `dpp20_program_blnd_lut()`, `dpp20_program_shaper()`, `dpp20_program_3dlut()`, cursor helpers, and `dpp2_cm_get_gamut_remap()`.
- The static caps object sets float-format DSCL processing and `dscl2_calc_lb_num_partitions()`.

## Control flow
`dpp201_cnv_setup()` starts by writing converter bypass and expansion mode, clears DCN20-style conversion defaults, maps the requested `surface_pixel_format` to a hardware pixel-format code, chooses default YCbCr color space and ICSC enablement for video formats, optionally writes the two-bit alpha LUT, writes pixel format and alpha enable fields, then calls `dpp1_program_input_csc()` with a DCN10-style `dcn10_input_csc_select`. Selected video formats force both cursor paths disabled. Finally it powers on OBUF through the DCN20 helper.

`dpp201_get_optimal_number_of_taps()` rejects some FP16 scaling on fixed-format DSCL caps and max-downscale source-width debug limits. It clamps exact 8.0 ratios down by one fixed-point unit because the hardware cannot program ratio 8 exactly. It fills default luma/chroma taps based on ratio ceilings, forces odd chroma horizontal taps down to the previous even value except tap 1, and reduces taps to 1 for identity ratios unless `debug.always_scale` is set.

Construction initializes the generic base, assigns the DCN201 function table and caps, stores generation-specific register tables, enables 18/24/30 bpp line-buffer depths, and records inherited line-buffer sizing constants.

## State and persistence behavior
State lives in the `struct dcn201_dpp` object and MMIO registers. The constructor sets in-memory pointers and caps. Converter setup writes persistent hardware state for the current mode until the next modeset/reset. Tap selection mutates the caller-provided `struct scaler_data` by filling `scl_data->taps` and adjusting exact-8 ratios. There is no durable persistence beyond runtime hardware state.

## Dependencies and integration points
The file depends on `dcn201_dpp.h`, inherited DCN20 register-field definitions, DCN10 CM/scaler helpers, DCN20 color and OBUF helpers, `reg_helper.h`, and display core pixel-format/scaler/debug types. It is the integration layer that lets DCN201 resource code instantiate a DPP while sharing most DCN10/DCN20 implementation.

## Risks and edge cases
This variant mixes DCN10 and DCN20 color helpers: setup uses `dpp1_program_input_csc()` and `dpp1_cm_set_gamut_remap()`, while the function table exposes DCN20 gamut readback. That split depends on DCN201 register compatibility and can be fragile if A/B bank fields differ. The FP16 scaling rejection condition uses width and height comparisons joined by `&&`; cases where only one dimension scales may bypass the rejection. `dpp201_cnv_setup()` ignores caller-provided `input_csc_color_matrix` adjustments and always passes NULL to `dpp1_program_input_csc()`, unlike DCN20 setup.

## Test signals
Tests should cover DCN201 construction, all pixel-format mappings, two-bit alpha LUT writes, cursor disable for packed/video formats, input CSC defaults for YCbCr formats, tap selection around identity ratios, exact 8.0 ratio clamping, odd chroma horizontal taps, debug `always_scale`, max-downscale rejection, FP16 scaling rejection, and inherited blend/shaper/3D LUT behavior through the function table.
