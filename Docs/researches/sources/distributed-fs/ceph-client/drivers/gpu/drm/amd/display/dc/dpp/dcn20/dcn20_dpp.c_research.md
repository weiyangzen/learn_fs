# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn20/dcn20_dpp.c

## Purpose
`dcn20_dpp.c` wires the DCN 2.0 DPP object into the generic display core. It implements DCN20-specific state readback, output-buffer power control, pixel-format converter setup, line-buffer partition math, alpha color keyer programming, cursor attribute programming, dummy legacy callbacks, the DCN20 DPP function table, caps, and constructor.

## Important APIs, types, and functions
- Lifecycle/integration APIs are `dpp20_read_state()`, `dpp2_construct()`, and the static `dcn20_dpp_funcs`/`dcn20_dpp_cap`.
- Power and setup APIs include `dpp2_power_on_obuf()` and the static `dpp2_cnv_setup()`.
- Scaler support is provided by `dscl2_calc_lb_num_partitions()` and `dscl2_spl_calc_lb_num_partitions()`, while actual scaler programming reuses `dpp1_dscl_set_scaler_manual_scale()`.
- Pixel/color conversion helpers include `dpp2_cnv_set_alpha_keyer()`, `dpp2_set_cursor_attributes()`, `dpp2_dummy_program_input_lut()`, and `oppn20_dummy_program_regamma_pwl()`.
- The function table binds DCN20 color APIs from `dcn20_dpp_cm.c` such as `dpp2_cm_set_gamut_remap()`, `dpp2_set_degamma_pwl()`, `dpp20_program_blnd_lut()`, `dpp20_program_shaper()`, and `dpp20_program_3dlut()`.

## Control flow
Construction fills the generic DPP base with context, instance, function table, and caps, then stores DCN20 register, shift, and mask tables. It enables all standard line-buffer depths and records the inherited line-buffer entry size/count.

`dpp2_cnv_setup()` configures the converter by clearing bypass, setting expansion mode and fixed format-control defaults, mapping `surface_pixel_format` enums to hardware pixel-format codes, choosing alpha enablement, picking default YCbCr color space for video formats, optionally programming the two-bit alpha LUT, writing `CNVC_SURFACE_PIXEL_FORMAT`, and invoking `dpp2_program_input_csc()` with either caller-provided CSC adjustment or default matrix selection. It disables cursor paths for selected packed/video formats and powers on OBUF/DSCL memory at the end.

`dpp20_read_state()` samples DPP enable, degamma mode, shaper mode, 3D LUT config, and blend gamma status into `struct dcn_dpp_state`. The line-buffer partition functions calculate how many luma/chroma/alpha lines fit for each memory config using DCN20 memory sizes and clamp results to 64.

## State and persistence behavior
State is held in the `struct dcn20_dpp` instance and in MMIO registers. The constructor initializes only in-memory object fields; setup functions program converter, cursor, keyer, power, and color/scaler registers. `dpp20_read_state()` exposes current hardware status for diagnostics or state reconstruction. There is no file-backed persistence.

## Dependencies and integration points
The file depends on `dcn20_dpp.h`, `dcn10_dpp.h` declarations reused through inheritance, `reg_helper.h`, display pixel-format/color enums, scaler structures, DC context debug state, and CM APIs implemented in `dcn20_dpp_cm.c`. It integrates with the display core through `struct dpp_funcs`, and with newer scaler-library paths through `dscl2_spl_calc_lb_num_partitions()`.

## Risks and edge cases
Pixel-format code mapping is hardware-specific and contains many packed/video formats; a wrong mapping produces corrupted scanout or incorrect channel order. For input CSC adjustment, the code copies twelve caller matrix entries but does not pass the custom table in the non-NULL-adjustment branch unless `tbl_entry` is correctly prepared, so this path is sensitive to local initialization and selection rules. Line-buffer math uses DCN20 constants and assumes 6 pixels per memory unit for luma/chroma/alpha. Dummy input LUT and regamma callbacks mean callers must use the DCN20 blend/shaper/3D LUT pipeline instead of legacy hooks.

## Test signals
Validation should cover DCN20 construction, state readback after modeset, all supported RGB/video pixel formats, two-bit alpha LUT programming, cursor disable behavior for 4:2:0 and selected 10-bit formats, OBUF power transitions, alpha color keyer ranges, line-buffer partition choices under scaling, and color pipeline tests that confirm blend/shaper/3D LUT callbacks are invoked instead of dummy legacy callbacks.
