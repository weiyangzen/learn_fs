# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn30/dcn30_dpp_cm.c

## Purpose
`dcn30_dpp_cm.c` implements the DCN3 DPP color-management functions that are separate from the main DPP file: CM bypass control, gamma-correction programmable LUT programming, CM dealpha/bias, HDR multiplier, and gamut-remap set/get.

## Important APIs, types, and functions
- `dpp3_program_gamcor_lut()` is the exported programmable gamma correction path for `dpp_funcs.dpp_program_gamcor_lut`.
- `dpp3_program_cm_dealpha()` and `dpp3_program_cm_bias()` program simple CM blending/bias registers.
- `dpp3_set_hdr_multiplier()` writes `CM_HDR_MULT_COEF`.
- `dpp3_cm_set_gamut_remap()` and `dpp3_cm_get_gamut_remap()` convert between DC fixed-point gamut matrices and hardware matrix registers.
- Local helpers include `dpp3_enable_cm_block()`, `dpp30_get_gamcor_current()`, `dpp3_program_gammcor_lut()`, `dpp3_power_on_gamcor_lut()`, `dpp3_gamcor_reg_field()`, `dpp3_configure_gamcor_lut()`, `program_gamut_remap()`, and `read_gamut_remap()`.

## Control flow
Gamma programming begins by enabling the CM block unless debug forces bypass. A NULL PWL parameter bypasses GAMCOR and schedules or performs memory power-down. A valid PWL parameter powers GAMCOR memory, sets programmable RAM mode, reads the currently active RAM bank, chooses the alternate bank, configures LUT host selection, selects the correct RAM A/B region and slope registers, fills `struct dcn3_xfer_func_reg` shift/mask metadata, calls `cm_helper_program_gamcor_xfer_func()`, writes LUT base values channel-by-channel or once if RGB values are equal, and finally updates `CM_GAMCOR_SELECT`.

Gamut remap accepts only software matrices. Non-software adjustment types bypass the block. Software matrices are converted to 12 hardware register values, the current active coefficient set is read, the alternate A/B set is selected, matrix registers are programmed through `cm_helper_program_color_matrices()`, and `CM_GAMUT_REMAP_MODE` is updated. Readback mirrors this by reading the current mode, reading the active matrix bank if not bypassed, and converting hardware matrix values back to `fixed31_32`.

## State and persistence behavior
State is transient and register-backed. GAMCOR RAM bank selection and gamut-remap coefficient set are maintained by hardware mode/current registers. The low-power path uses `dpp_base->deferred_reg_writes.bits.disable_gamcor` and `ctx->dc->optimized_required` to defer memory shutdown until a safe update point. No file or firmware persistence exists.

## Dependencies and integration points
The file depends on `dcn30_dpp.h`, `dcn30_cm_common.h`, conversion helpers, `reg_helper`, and Display Core color structures. It is wired into `dcn30_dpp_funcs` and reused by later DPP constructors unless a later generation explicitly removes the callback. It also relies on DC debug flags such as `cm_in_bypass`, `enable_mem_low_power.bits.cm`, and DC caps such as `ips_v2_support`.

## Risks and edge cases
GAMCOR programming is sensitive to bank selection, region register mapping, and low-power sequencing. `params` must contain valid PWL point counts and curve metadata; the LUT writer indexes `rgb[num - 1]`. The function name `dpp3_program_gammcor_lut()` has a typo but is local. Gamut remap assumes only two coefficient sets and always alternates based on current mode; unexpected hardware modes fall back to set A. Color matrix conversion precision and signedness are important for visual correctness.

## Test signals
Relevant validation includes gamma LUT updates with RAM A/B alternation, NULL gamma bypass and low-power defer tests, CM bypass debug mode, HDR multiplier programming, gamut-remap set/get round trips, visual CRC/colorimeter validation for color temperature matrices, and resume/retrain scenarios where current-mode registers must still reflect software expectations.
