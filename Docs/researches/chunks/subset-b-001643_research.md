# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_1_sh_mask.h lines 5078-7595

## Purpose

This chunk is part of the generated DCN 2.0.1 register shift/mask header for the AMDGPU display engine. It contains no executable C code; it defines `#define` constants that describe bit positions and masks for display pipe processor (DPP) registers. The driver uses these constants to build per-ASIC `shift` and `mask` tables, then accesses fields through the `REG_GET`, `REG_SET`, `REG_UPDATE`, and related register-helper macros.

The assigned range starts in the middle of the DPP0 color-management (`CM0`) blend-gamma RAM-B region definitions, then covers DPP0 shaper, 3D LUT, and color-management memory-power fields. It then defines the DPP1 top, converter, cursor, scaler, and full color-management field set, and ends at the beginning of the DPP2 scaler block after `DSCL2_SCL_HORZ_FILTER_INIT`.

The highest-value content is the DPP1 block because it is complete in this range: `DPP_TOP1`, `CNVC_CFG1`, `CNVC_CUR1`, `DSCL1`, and `CM1` masks collectively describe the programmable path from source pixel format conversion, cursor handling, scaling/filter coefficient RAM, color-space/gamma/LUT processing, and DPP diagnostics.

## Important APIs, Types, And Macros

- `*_SHIFT` macros: give the right-shift amount for a named register field. Examples include `CM1_CM_SHAPER_CONTROL__CM_SHAPER_LUT_MODE__SHIFT`, `CNVC_CFG1_FORMAT_CONTROL__ALPHA_EN__SHIFT`, and `DSCL1_SCL_MODE__SCL_COEF_RAM_SELECT__SHIFT`.
- `*_MASK` macros: give the bit mask for the same field. These are paired with the shift constants by the register-helper layer.
- `CM0_*`, `CM1_*`: color-management field definitions for blend gamma, degamma, shaper LUTs, 3D LUT, input CSC, gamut remap, bias, HDR multiplier, coefficient format, de-alpha, and color-management memory power.
- `DPP_TOP1_*` and `DPP_TOP2_*`: DPP control, clock enable, reset, CRC value/control, and host-read-rate field definitions.
- `CNVC_CFG1_*` and `CNVC_CFG2_*`: converter configuration fields for source pixel format, expansion, alpha, bypass/alignment, clamping, floating-point bias/scale, color keying, and 2-bit alpha LUT entries.
- `CNVC_CUR1_*` and `CNVC_CUR2_*`: cursor-control fields for enable, cursor mode, ROM degamma enable, pixel inversion, alpha modulation, colors, and FP scale/bias.
- `DSCL1_*` and `DSCL2_*`: display scaler fields for coefficient RAM addressing/data, scaler mode, tap counts, 2-tap controls, manual replication, scale ratios, initial filter phase, overscan, recout/MPC size, line-buffer format/memory, OBUF power, and scaler memory power.
- Integration macros outside this file, especially `TF_REG_LIST_DCN201(id)` and `TF_REG_LIST_SH_MASK_DCN201(mask_sh)` in `display/dc/dpp/dcn201/dcn201_dpp.h`, alias the DCN 2.0 DPP register and field lists and consume these generated symbols.

## Register Families Covered

- DPP0 color-management tail, lines 5078-5647: completes `CM0_CM_BLNDGAM_RAMB_REGION_18_19` through `_32_33`, then defines `CM0` HDR multiplier, shared/blend-gamma memory-power control and status, de-alpha, coefficient format, shaper LUT control/data/write-enable, shaper RAM A/B region maps, shaper memory-power controls/status, 3D LUT mode/index/data/read-write controls, output normalization/offsets, and test debug index/data.
- DPP1 top/control, lines 5648-5714: `DPP_TOP1_DPP_CONTROL` exposes clock enable, input/output enable, and read-only enable/status fields; `DPP_TOP1_DPP_SOFT_RESET` covers DPP and CM reset bits; CRC registers expose RGB/A captured values and CRC mode/source/stereo/interlace/pixel-format controls.
- DPP1 converter and cursor, lines 5715-5818: `CNVC_CFG1_*` configures source pixel interpretation and color keying; `CNVC_CUR1_*` configures cursor0 modes and colors.
- DPP1 scaler, lines 5819-6055: `DSCL1_*` defines coefficient RAM programming, scaler mode and coefficient RAM bank selection, tap counts, filter scale ratios/initial phases, overscan, recout/MPC geometry, line-buffer configuration/status, scaler LUT memory power/status, output buffer control, and OBUF memory power.
- DPP1 color management, lines 6056-7356: `CM1_*` mirrors the full color pipeline, including input CSC and gamut-remap matrices, bias, degamma LUT RAM A/B region tables, blend-gamma LUT RAM A/B region tables, shaper LUT RAM A/B region tables, HDR/3D LUT controls, memory-power controls/status, and output offsets.
- DPP2 beginning, lines 7357-7595: defines the same DPP top, converter, cursor, and early scaler coefficient/mode/tap/ratio fields for instance 2. The range ends before the rest of `DSCL2` is defined.

## Control Flow

There is no runtime control flow in this header. The effective flow is compile-time table construction followed by runtime register-helper calls:

1. `display/dc/resource/dcn201/dcn201_resource.c` includes `dcn_2_0_1_sh_mask.h`.
2. `dcn201_resource.c` builds `tf_shift` with `TF_REG_LIST_SH_MASK_DCN201(__SHIFT)` and `tf_mask` with `TF_REG_LIST_SH_MASK_DCN201(_MASK)`.
3. `dcn201_dpp.h` maps `TF_REG_LIST_SH_MASK_DCN201()` to `TF_REG_LIST_SH_MASK_DCN20()`, so the DCN 2.0 DPP field list is populated from symbols such as `CM0_CM_SHAPER_CONTROL__CM_SHAPER_LUT_MODE__SHIFT` and `CNVC_CFG0_FORMAT_CONTROL__ALPHA_EN_MASK`. Per-instance register addresses are separately built through `TF_REG_LIST_DCN201(id)`.
4. Runtime code in `dcn201_dpp.c`, `dcn20_dpp.c`, `dcn20_dpp_cm.c`, and inherited DCN10 scaler helpers uses `REG_UPDATE`, `REG_SET`, and `REG_GET` with field names. The helper layer looks up the shift/mask values in the DPP object and emits masked MMIO reads/writes.

The DPP1 and DPP2 symbols in this chunk are generated instance-specific equivalents of the instance-0 symbols used to populate shared field lists. They matter for direct instance-specific register maps and for consistency across generated DCN register headers, even when the common DPP field table is anchored on the `CM0`, `CNVC_CFG0`, and `DSCL0` naming pattern.

## State And Persistence Behavior

The header itself owns no software state and performs no reads or writes. Its state effect is indirect: every mask and shift controls how later driver code mutates hardware MMIO registers. Those register writes persist in display hardware until changed by another modeset/color update, power transition, or hardware reset.

The fields in this chunk describe several hardware state machines and RAM-backed blocks:

- Color LUT state persists in DPP-local degamma, blend-gamma, shaper, and 3D LUT RAMs. Region tables define LUT offsets, segment counts, start/end points, base values, slopes, and active RAM bank selection.
- Converter state persists pixel-format, alpha, clamping, color-key range, and 2-bit alpha LUT settings for each pipe.
- Scaler state persists coefficient RAM contents, selected coefficient bank, tap counts, scale ratios, initial phases, overscan, line-buffer format, and memory-power overrides/status.
- Cursor state persists cursor mode, enable, color registers, ROM enable, pixel inversion, and FP scale/bias.
- Diagnostic state includes DPP CRC controls and captured CRC values.

Because fields are packed into shared 32-bit registers, an incorrect mask or shift can corrupt adjacent hardware state during a read-modify-write operation.

## Dependencies

This generated header depends on the DCN 2.0.1 ASIC register specification and must stay aligned with the paired address header `dcn_2_0_1_offset.h` and higher-level DPP register lists. The driver-side dependencies are:

- `display/dc/resource/dcn201/dcn201_resource.c`, which includes this file and instantiates DPP register, shift, and mask tables for DCN 2.0.1 resources.
- `display/dc/dpp/dcn201/dcn201_dpp.h`, which reuses DCN 2.0 DPP register and field-list macros for DCN 2.0.1.
- `display/dc/dpp/dcn201/dcn201_dpp.c`, which wires the DPP function table and uses the populated tables for setup, scaler programming, color functions, cursor functions, and alpha keying.
- `display/dc/dpp/dcn20/dcn20_dpp.c` and `display/dc/dpp/dcn20/dcn20_dpp_cm.c`, which provide shared DCN20-era implementations for state readback, converter setup, color keying, cursor attributes, HDR multiplier, degamma, blend LUT, shaper LUT, and 3D LUT programming.
- `display/dc/dpp/dcn10/dcn10_dpp_dscl.c`, inherited for scaler coefficient RAM programming and scaler setup paths that use `DSCL*_SCL_*` masks and shifts.
- `reg_helper.h` and the display MMIO service layer, which combine register offsets, masks, and shifts into actual MMIO transactions.

## Integration Points

The primary integration point is DCN201 resource creation. `dcn201_resource.c` allocates four DPP instances and passes the per-instance `tf_regs[]`, shared `tf_shift`, and shared `tf_mask` tables into `dpp201_construct()`. From there, each `struct dcn201_dpp` uses these tables through the DPP function table.

Important runtime paths connected to this chunk include:

- Plane setup: `dpp201_cnv_setup()` programs `FORMAT_CONTROL`, `CNVC_SURFACE_PIXEL_FORMAT`, `ALPHA_2BIT_LUT`, cursor disable bits for unsupported YUV layouts, and powers on OBUF/scaler LUT memory.
- Alpha/color keying: `dpp2_cnv_set_alpha_keyer()` writes `COLOR_KEYER_CONTROL` and low/high channel ranges for alpha, red, green, and blue.
- Cursor configuration: `dpp2_set_cursor_attributes()` writes `CURSOR0_CONTROL`, `CURSOR0_COLOR0`, and `CURSOR0_COLOR1`; inherited cursor position code also relies on compatible cursor register tables.
- Scaler programming: inherited scaler helpers write `SCL_COEF_RAM_TAP_SELECT`, `SCL_COEF_RAM_TAP_DATA`, `SCL_MODE`, tap controls, scale ratios, initial phases, line-buffer controls, and scaler memory-power bits.
- Color pipeline: `dpp20_read_state()` reads shaper, 3D LUT, and blend-gamma status; `dpp2_set_degamma_pwl()`, `dpp20_program_blnd_lut()`, `dpp20_program_shaper()`, and `dpp20_program_3dlut()` rely on the CM LUT, region, RAM-select, write-enable, and status fields represented here.
- Diagnostics and bring-up: `DPP_TOP*_DPP_CRC_*`, `DPP_TOP*_DPP_SOFT_RESET`, and host-read controls are exposed for state readback, validation, and low-level debug.

## Risks And Edge Cases

- This file is generated hardware interface data. Manual edits are risky because a one-bit error in a mask or shift can make register-helper read-modify-write calls program the wrong field while still compiling cleanly.
- The requested range starts mid-family at `CM0_CM_BLNDGAM_RAMB_REGION_18_19`; the earlier `CM0` blend-gamma control, RAM-A, and RAM-B region definitions are outside this chunk. Any final per-file report must reconcile this chunk with adjacent chunks before describing the full DPP0 color path.
- The range ends inside the `DSCL2` scaler block after `DSCL2_SCL_HORZ_FILTER_INIT`; later DPP2 vertical filter, line-buffer, memory-power, and OBUF fields are outside this chunk.
- Instance naming is repetitive and easy to mismatch. `CM1_*`, `CNVC_CFG1_*`, and `DSCL1_*` must correspond to DPP instance 1 register addresses; substituting an instance 0 or 2 symbol in a register list would direct writes to the wrong pipe.
- LUT programming depends on bank selection/status fields. Wrong `*_WRITE_SEL`, `*_RAM_SEL`, `*_CONFIG_STATUS`, or `*_MODE_CURRENT` masks can cause the driver to update a currently active LUT bank or read stale status.
- Power-management fields such as `CM*_CM_MEM_PWR_CTRL*`, `DSCL*_DSCL_MEM_PWR_CTRL`, and `OBUF_MEM_PWR_CTRL` can gate SRAMs used by later programming. Incorrect values can cause timeouts, blank output, or lost LUT/coef RAM contents.
- Scaler coefficient fields pack two signed coefficients and enable bits into one word. Incorrect masks for `SCL_COEF_RAM_EVEN_TAP_COEF`, `SCL_COEF_RAM_ODD_TAP_COEF`, or their enable bits can produce image-quality regressions rather than obvious failures.
- CRC and host-read controls are diagnostic-facing but can affect validation. Incorrect CRC source, pixel-format, stereo, cursor, or mask fields would make hardware CRC tests misleading.

## Test Signals

- Build coverage: compile the AMDGPU display driver for a DCN201-enabled configuration. The generated symbols must satisfy `TF_REG_LIST_SH_MASK_DCN201(__SHIFT)` and `_MASK` table initialization without missing-field errors.
- Modeset smoke tests on DCN 2.0.1 hardware: attach displays, enable multiple planes, move/scale planes, and verify no blanking or DPP power/timeout errors.
- Pixel-format coverage: exercise ARGB/RGB formats, FP16 formats, 4:2:0 YCbCr/YCrCb formats, 10-bit formats, and 2-bit alpha LUT cases that drive `CNVC_CFG*` fields.
- Cursor tests: enable mono and color cursors, toggle cursor degamma/ROM behavior, and verify cursor disable behavior on formats where the DPP setup forces cursor off.
- Scaling tests: cover identity, upscaling, downscaling, chroma scaling, even/one-tap cases, and coefficient RAM bank switching. Visual inspection and CRC comparison should catch wrong `DSCL*` masks.
- Color tests: program degamma, blend gamma, shaper LUT, 3D LUT, HDR multiplier, gamut remap, and bypass modes, then compare hardware CRCs or captured output against reference images.
- Power-management tests: suspend/resume, display power-gating, and repeated modesets should preserve or correctly reprogram CM/scaler SRAM state after memory-power transitions.
- Diagnostics: DPP CRC readback should change predictably with source selection, pixel-format selection, cursor inclusion, and CRC mask fields.
