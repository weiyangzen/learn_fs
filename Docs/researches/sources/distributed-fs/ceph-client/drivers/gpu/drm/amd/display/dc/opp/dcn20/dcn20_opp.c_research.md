# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/opp/dcn20/dcn20_opp.c

## Purpose
`dcn20_opp.c` extends the DCN10 OPP implementation with DCN2.0 display pattern generator support, DPG blank-color helpers, DPG pending/blanked status checks, 4:2:2 left-edge extra-pixel programming, and expanded register readback.

## Important APIs, types, and functions
DCN20-specific functions include `opp2_set_disp_pattern_generator()`, `opp2_program_dpg_dimensions()`, `opp2_dpg_set_blank_color()`, `opp2_dpg_is_blanked()`, `opp2_dpg_is_pending()`, `opp2_program_left_edge_extra_pixel()`, `opp2_get_left_edge_extra_pixel_count()`, `opp2_read_reg_state()`, and `dcn20_opp_construct()`. The function table reuses DCN10 format, dynamic-expansion, stereo, pipe-clock, and destroy functions.

## Control flow
Pattern programming starts by translating requested color depth to DPG bit-depth, then writes active dimensions and offset. Color-square modes choose VESA/CEA dynamic range and RGB/YCbCr601/YCbCr709 mode. Bar modes scale 16-bit white/black source colors to the requested bpc, left-align the data in DPG color registers, and enable vertical or horizontal bars. Color-ramp mode computes ramp increments from source and destination bpc. Video mode disables DPG state, and solid-color mode programs both color slots to the supplied blank color before enabling a horizontal-bar generator. Left-edge extra-pixel programming writes one extra pixel only for non-primary 4:2:2/4:2:0 paths when 1-tap subsampling is not forced.

## State and persistence behavior
State is hardware-resident in DPG, FMT_422, OPPBUF, OPP_PIPE, and DSCRM registers. `struct dcn20_opp` stores register metadata and inherits the OPP base; there is no persistent state outside runtime memory and register programming.

## Dependencies and integration points
The file depends on DCN10 OPP helpers, DPG register definitions, `controller_dp_test_pattern`, `controller_dp_color_space`, `dc_color_depth`, `tg_color`, and debug flags under the DC context. It integrates with link training/test-pattern flows, blanking flows, and chroma-subsampling pipe programming.

## Risks and edge cases
DPG color values must be left-aligned to the hardware format; wrong shifts cause visibly incorrect patterns. `opp2_dpg_is_blanked()` checks DPG enable and double-buffer pending rather than color content. Left-edge extra-pixel behavior depends on primary/secondary pipe roles and debug overrides. Solid color uses horizontal bars with identical colors, so accidental mismatched color slots would show a pattern.

## Test signals
DP test-pattern compliance for color squares, CEA color squares, bars, ramps, video mode, and solid color; DPG pending/blanked polling; 4:2:2 and 4:2:0 secondary-pipe chroma tests; and readback of `DSCRM_DSC_FORWARD_CONFIG` and FMT/DPG registers provide useful validation.
