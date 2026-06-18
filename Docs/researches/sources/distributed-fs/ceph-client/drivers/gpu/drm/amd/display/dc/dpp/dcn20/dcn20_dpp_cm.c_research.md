# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn20/dcn20_dpp_cm.c

## Purpose
`dcn20_dpp_cm.c` implements the DCN 2.0 DPP color-management pipeline. It adapts degamma and CSC/gamut programming to DCN20 register status fields, adds blend gamma and shaper LUT programming, and programs the DCN20 3D LUT in either 17x17x17 or 9x9x9 layout with 10-bit or 12-bit channel storage.

## Important APIs, types, and functions
- Degamma APIs are `dpp2_set_degamma_pwl()` and `dpp2_set_degamma()`, backed by `dpp2_degamma_ram_inuse()` and `dpp2_program_degamma_lut()`.
- Gamut APIs are `dpp2_cm_set_gamut_remap()` and `dpp2_cm_get_gamut_remap()`, backed by DCN20 A/B `program_gamut_remap()` and `read_gamut_remap()`.
- Input CSC is handled by `dpp2_program_input_csc()`.
- Blend gamma APIs are `dpp20_program_blnd_lut()`, `dpp20_get_blndgam_current()`, `dpp20_configure_blnd_lut()`, and RAM A/B metadata/payload helpers.
- Shaper APIs are `dpp20_program_shaper()`, `dpp20_get_shaper_current()`, `dpp20_configure_shaper_lut()`, `dpp20_program_shaper_lut()`, and RAM A/B settings helpers.
- 3D LUT APIs are `dpp20_program_3dlut()`, `get3dlut_config()`, `dpp20_set_3dlut_mode()`, `dpp20_select_3dlut_ram()`, `dpp20_select_3dlut_ram_mask()`, `dpp20_set3dlut_ram12()`, and `dpp20_set3dlut_ram10()`.
- `dpp2_set_hdr_multiplier()` writes the DCN20 HDR multiplier field.

## Control flow
Degamma PWL programming is similar to DCN10 but detects the active bank from `CM_DGAM_CONFIG_STATUS` in `CM_DGAM_LUT_WRITE_EN_MASK`. It powers degamma memory through the inherited DCN10 helper, enables the CM block subject to the debug `cm_in_bypass` flag, writes the inactive RAM's transfer-function metadata and LUT payload, then flips selection with `dpp1_degamma_ram_select()`.

Gamut remap and input CSC both use DCN20 debug status index 9 through `IX_REG_GET()`. If bypass is requested they set the mode to zero. Otherwise they read the active A/B selection, program the inactive A or B register bank, and then switch the mode field. Matrix values come from caller adjustments or from `dpp_input_csc_matrix`.

Blend and shaper LUTs follow the same double-buffer model. A NULL parameter disables the block. Otherwise the current config status selects the next RAM, write masks and indices are set, transfer-function region metadata is programmed for that bank, payload values are streamed to data registers, and the mode is switched to RAM A or RAM B. The shaper packs base and delta fields into one 24-bit-ish value per color write.

`dpp20_program_3dlut()` disables on NULL, otherwise selects the inactive 3D LUT RAM, chooses 17-cube or 9-cube data from `tetrahedral_params`, chooses 10-bit packed or 12-bit paired write format, writes four LUT planes by changing the RAM selection mask, and finally enables the selected RAM/size in `CM_3DLUT_MODE`.

## State and persistence behavior
State is volatile and mostly banked in hardware. Current bank/mode status is read from config status fields before programming. LUT payloads, region metadata, and CSC matrices live in MMIO-backed RAM/register banks. No C-level persistent cache is maintained in this file; synchronization relies on hardware status fields and mode switches.

## Dependencies and integration points
The file depends on `dcn20_dpp.h`, inherited DCN10 degamma metadata helpers, `dcn10_cm_common.h`, `reg_helper.h`, fixed-point conversion helpers, `dc_lut_mode`, `pwl_params`, `tetrahedral_params`, and common CSC matrix tables. It supplies most DCN20 color callbacks installed by `dcn20_dpp.c` and reused by `dcn201_dpp.c`.

## Risks and edge cases
Bank switching is sensitive to status encodings: blend/shaper status 1/2 and gamut/ICSC A/B values must match hardware. NULL parameters disable blocks, so callers must avoid accidental NULL during transitions. The 3D LUT 12-bit path writes entries two at a time and indexes `lut[i+1]`; it assumes an even entry count. The 10-bit path packs channels into 30 bits and depends on input values already fitting 10 bits. The `is_color_channel_12bits` argument to `dpp20_set_3dlut_mode()` is unused there, with bit-depth controlled instead by the read/write control register.

## Test signals
Relevant tests include degamma PWL bank flips, gamut/input CSC A/B readback, blend LUT enable/disable and bank alternation, shaper LUT payload/segment programming, 3D LUT 17 and 9 tetrahedral modes, 10-bit and 12-bit channel writes, NULL-to-bypass transitions, HDR multiplier updates, and visual or CRC tests for HDR/color-managed planes across repeated atomic commits.
